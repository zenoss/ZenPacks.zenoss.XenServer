##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import logging
LOG = logging.getLogger('zen.XenServer')

from collections import defaultdict, OrderedDict

from twisted.internet.defer import inlineCallbacks, returnValue

from Products.DataCollector.plugins.DataMaps import MultiArgs, ObjectMap, RelationshipMap

from ZenPacks.zenoss.XenServer import MODULE_NAME
from ZenPacks.zenoss.XenServer.utils import id_from_ref
from ZenPacks.zenoss.XenServer.SR import SR
from ZenPacks.zenoss.XenServer.VDI import VDI
from ZenPacks.zenoss.XenServer.Host import Host
from ZenPacks.zenoss.XenServer.HostCPU import HostCPU
from ZenPacks.zenoss.XenServer.PBD import PBD
from ZenPacks.zenoss.XenServer.PIF import PIF
from ZenPacks.zenoss.XenServer.Network import Network
from ZenPacks.zenoss.XenServer.VM import VM
from ZenPacks.zenoss.XenServer.VBD import VBD
from ZenPacks.zenoss.XenServer.VIF import VIF
from ZenPacks.zenoss.XenServer.VMAppliance import VMAppliance
from ZenPacks.zenoss.XenServer.Pool import Pool


__all__ = ['DataMapProducer']


XENAPI_CLASSMAP = {
    'sr': SR,
    'vdi': VDI,
    'host_metrics': Host,
    'host': Host,
    'host_cpu': HostCPU,
    'pbd': PBD,
    'pif_metrics': PIF,
    'pif': PIF,
    'network': Network,
    'vm_metrics': VM,
    'vm': VM,
    'vbd': VBD,
    'vif': VIF,
    'vm_appliance': VMAppliance,
    'pool': Pool,
    }


def merge_objectmaps(objectmaps):
    '''
    Merge attributes from ObjectMaps with identical ids.
    '''
    merged = OrderedDict()
    for id_, objectmap in ((x.id, x) for x in objectmaps):
        if id_ in merged:
            objectmap.updateFromDict(merged[id_])

        merged[id_] = objectmap

    return merged.values()


class DataMapProducer(object):
    def __init__(self, client):
        self.client = client
        self.last_token = ''
        self.backrefs = {}
        self.parentrefs = {}

    @inlineCallbacks
    def getmaps(self, timeout=0.0):
        '''
        Return a datamaps iterable.

        The first time this method is called the returned iterable will
        contain datamaps sufficent to fully model the endpoint.
        Subsequent calls will return datamaps sufficient to update the
        previous model to the current model.
        '''
        records = yield self.client.xenapi.event['from'](
            XENAPI_CLASSMAP.keys(), self.last_token, float(timeout))

        if not records:
            returnValue([])

        # We only care about the most recent event for each ref.
        events = OrderedDict()
        for event in records['events']:
            LOG.debug(
                "event operation '%s' processing: %s",
                event['operation'], event)

            events[event['ref']] = event

        if self.last_token:
            maps = self.incremental_datamaps(events.values())
        else:
            maps = self.full_datamaps(events.values())

        # Store last token for next time.
        self.last_token = records['token']

        returnValue(maps)

    def get_objectmap(self, event):
        '''
        Return the appropriate ObjectMap for event.
        '''
        model_class = XENAPI_CLASSMAP.get(event['class'])
        if not model_class:
            # This is not an object type we care about.
            return

        # Building the ObjectMap differs for _metrics classes
        # because they unfortunately don't contain their own back-
        # reference to the object they provide metrics for.
        if event['class'].endswith('_metrics'):
            if 'snapshot' not in event:
                # No sense processing a metric with no snapshot.
                return

            ref = self.backrefs.get(event['ref'])
            if not ref:
                # The container for this object doesn't exist.
                return

            model_method = model_class.objectmap_metrics
        else:
            ref = event['ref']
            model_method = model_class.objectmap

            # Nested components need some help in knowing their parent.
            if 'snapshot' not in event:
                parent = self.parentrefs.get(ref)
                if parent:
                    event['snapshot'] = {'parent': parent}

        data = model_method(ref, event.get('snapshot'))
        if data:
            return ObjectMap(data=data, modname=model_class.__module__)

    def full_datamaps(self, events):
        '''
        Return a list of datamaps representing a full model.
        '''
        sr_oms = []
        vdi_oms = defaultdict(list)
        host_oms = []
        host_cpu_oms = defaultdict(list)
        pbd_oms = defaultdict(list)
        pif_oms = defaultdict(list)
        network_oms = []
        vm_oms = []
        vbd_oms = defaultdict(list)
        vif_oms = defaultdict(list)
        vm_appliance_oms = []
        pool_oms = []

        # Used to prevent yielding multiple endpoint.os ObjectMaps.
        os_om_flag = False

        for event in events:
            if event['operation'] == 'del':
                # There should be no delete events in a full model.
                continue

            om = self.get_objectmap(event)
            if not om:
                continue

            if event['class'] == 'sr':
                sr_oms.append(om)

                # Initialize contained objmap lists.
                vdi_oms.setdefault(event['ref'], [])

            elif event['class'] == 'vdi':
                sr_ref = event['snapshot']['SR']
                vdi_oms[sr_ref].append(om)

                # Need to track this to handle subcomponent deletion.
                self.parentrefs[event['ref']] = sr_ref

            elif event['class'] == 'host':
                host_oms.append(om)

                # Initialize contained objmap lists.
                host_cpu_oms.setdefault(event['ref'], [])
                pbd_oms.setdefault(event['ref'], [])
                pif_oms.setdefault(event['ref'], [])

                # Save metric -> host mapping for host_metrics events.
                host_metrics_ref = event['snapshot']['metrics']
                self.backrefs[host_metrics_ref] = event['ref']

                # Build the endpoint's os ObjectMap from the first host
                # data we see.
                if not os_om_flag:
                    os_om_flag = True
                    yield self.objectmap_endpoint_os(event['snapshot'])

            elif event['class'] == 'host_metrics':
                host_oms.append(om)

            elif event['class'] == 'host_cpu':
                host_ref = event['snapshot']['host']
                host_cpu_oms[host_ref].append(om)

                # Need to track this to handle subcomponent deletion.
                self.parentrefs[event['ref']] = host_ref

            elif event['class'] == 'pbd':
                host_ref = event['snapshot']['host']
                pbd_oms[host_ref].append(om)

                # Need to track this to handle subcomponent deletion.
                self.parentrefs[event['ref']] = host_ref

            elif event['class'] == 'pif':
                host_ref = event['snapshot']['host']
                pif_oms[host_ref].append(om)

                # Save metric -> pif mapping for pif_metrics events.
                pif_metrics_ref = event['snapshot']['metrics']
                self.backrefs[pif_metrics_ref] = (
                    event['ref'], event['snapshot']['host'])

                # Need to track this to handle subcomponent deletion.
                self.parentrefs[event['ref']] = host_ref

            elif event['class'] == 'pif_metrics':
                host_ref = self.backrefs[event['ref']][1]
                pif_oms[host_ref].append(om)

            elif event['class'] == 'network':
                network_oms.append(om)

            elif event['class'] == 'vm':
                vm_oms.append(om)

                # Initialize contained objmap lists.
                vbd_oms.setdefault(event['ref'], [])
                vif_oms.setdefault(event['ref'], [])

                # Save metric -> vm mapping for vm_metrics events.
                vm_metrics_ref = event['snapshot']['metrics']
                self.backrefs[vm_metrics_ref] = event['ref']

            elif event['class'] == 'vm_metrics':
                vm_oms.append(om)

            elif event['class'] == 'vbd':
                vm_ref = event['snapshot']['VM']
                vbd_oms[vm_ref].append(om)

                # Need to track this to handle subcomponent deletion.
                self.parentrefs[event['ref']] = vm_ref

            elif event['class'] == 'vif':
                vm_ref = event['snapshot']['VM']
                vif_oms[vm_ref].append(om)

                # Need to track this to handle subcomponent deletion.
                self.parentrefs[event['ref']] = vm_ref

            elif event['class'] == 'vm_appliance':
                vm_appliance_oms.append(om)

            elif event['class'] == 'pool':
                pool_oms.append(om)

        yield RelationshipMap(
            relname='srs',
            modname=MODULE_NAME['SR'],
            objmaps=sr_oms)

        for parent_ref, objmaps in vdi_oms.iteritems():
            yield RelationshipMap(
                compname='srs/{}'.format(id_from_ref(parent_ref)),
                relname='vdis',
                modname=MODULE_NAME['VDI'],
                objmaps=objmaps)

        yield RelationshipMap(
            relname='hosts',
            modname=MODULE_NAME['Host'],
            objmaps=merge_objectmaps(host_oms))

        for parent_ref, objmaps in host_cpu_oms.iteritems():
            yield RelationshipMap(
                compname='hosts/{}'.format(id_from_ref(parent_ref)),
                relname='hostcpus',
                modname=MODULE_NAME['HostCPU'],
                objmaps=objmaps)

        for parent_ref, objmaps in pbd_oms.iteritems():
            yield RelationshipMap(
                compname='hosts/{}'.format(id_from_ref(parent_ref)),
                relname='pbds',
                modname=MODULE_NAME['PBD'],
                objmaps=objmaps)

        for parent_ref, objmaps in pif_oms.iteritems():
            yield RelationshipMap(
                compname='hosts/{}'.format(id_from_ref(parent_ref)),
                relname='pifs',
                modname=MODULE_NAME['PIF'],
                objmaps=merge_objectmaps(objmaps))

        yield RelationshipMap(
            relname='networks',
            modname=MODULE_NAME['Network'],
            objmaps=network_oms)

        yield RelationshipMap(
            relname='vms',
            modname=MODULE_NAME['VM'],
            objmaps=merge_objectmaps(vm_oms))

        for parent_ref, objmaps in vbd_oms.iteritems():
            yield RelationshipMap(
                compname='vms/{}'.format(id_from_ref(parent_ref)),
                relname='vbds',
                modname=MODULE_NAME['VBD'],
                objmaps=objmaps)

        for parent_ref, objmaps in vif_oms.iteritems():
            yield RelationshipMap(
                compname='vms/{}'.format(id_from_ref(parent_ref)),
                relname='vifs',
                modname=MODULE_NAME['VIF'],
                objmaps=objmaps)

        yield RelationshipMap(
            relname='vmappliances',
            modname=MODULE_NAME['VMAppliance'],
            objmaps=vm_appliance_oms)

        yield RelationshipMap(
            relname='pools',
            modname=MODULE_NAME['Pool'],
            objmaps=pool_oms)

    def incremental_datamaps(self, events):
        '''
        Generate datamaps representing incremental model updates.
        '''
        for event in events:
            om = self.get_objectmap(event)
            if not om:
                continue

            if event['operation'] == 'del':
                om.remove = True
                yield om
                continue

            # Incremental parent ref tracking.
            parent_key = {
                'vdi': 'SR',
                'host_cpu': 'host',
                'pbd': 'host',
                'pif': 'host',
                'vbd': 'VM',
                'vif': 'VM',
                }.get(event['class'])

            if parent_key:
                self.parentrefs[event['ref']] = event['snapshot'][parent_key]

            yield om

    def objectmap_endpoint_os(self, host_properties):
        '''
        Return an ObjectMap for endpoint.os given XAPI host properties.
        '''
        manufacturer = host_properties.get('API_version_vendor')
        version_major = host_properties.get('API_version_major')
        version_minor = host_properties.get('API_version_minor')

        if manufacturer and version_major and version_minor:
            model = 'XenAPI %s.%s' % (version_major, version_minor)

        return ObjectMap(data={
            'setProductKey': MultiArgs(model, manufacturer),
            }, compname='os')
