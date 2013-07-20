##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

'''
Model XenServer pools using XenAPI (a.k.a. XAPI).
'''

import logging
LOG = logging.getLogger('zen.XenServer')

import collections

from twisted.internet.defer import DeferredList, inlineCallbacks, returnValue

from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import MultiArgs, ObjectMap, RelationshipMap
from Products.ZenUtils.Utils import prepId

from ZenPacks.zenoss.XenServer import MODULE_NAME
from ZenPacks.zenoss.XenServer.utils import add_local_lib_path

# Allows txxenapi to be imported.
add_local_lib_path()

import txxenapi


XAPI_CLASSES = [
    'SR',
    'VDI',
    'host',
    'host_cpu',
    'PBD',
    'PIF',
    'network',
    'VM',
    'VBD',
    'VIF',
    'VM_appliance',
    'pool',
    ]


def id_from_ref(ref):
    '''
    Return a component id given a XenAPI OpaqueRef.
    '''
    if not ref or ref == 'OpaqueRef:NULL':
        return None

    return prepId(ref.split(':', 1)[1])


def ids_from_refs(refs):
    '''
    Return list of component ids given a list of XenAPI OpaqueRefs.

    Null references won't be included in the returned list. So it's
    possible that the returned list will be shorter than the passed
    list.
    '''
    ids = []

    for ref in refs:
        id_ = id_from_ref(ref)
        if id_:
            ids.append(id_)

    return ids


class ModelerPluginCacheMixin(object):
    '''
    Mix-in class to allow modeler plugin instances to safely share an
    instance level class per modeling run.

    This is used for when methods need to share data. It is required
    because this modeler plugin instance is persistent across modeling
    cycles and can be used to model multiple devices.
    '''

    def cache_prepare(self, device):
        '''
        Prepare class cache for modeling device.
        '''
        self.device = device
        if not hasattr(self, 'cache'):
            self.cache = {}

        self.cache[self.device.id] = collections.defaultdict(dict)

    def cache_set(self, namespace, key, value):
        '''
        Set the cache value for key in namespace. Return value.
        '''
        if not self.device or not self.cache:
            raise Exception('cache not initialized')

        self.cache[self.device.id][namespace][key] = value

        return value

    def cache_get(self, namespace, key, default=None):
        '''
        Get the cached value for key in namespace.
        '''
        if not self.device or not self.cache:
            raise Exception('cache not initialized')

        return self.cache[self.device.id][namespace].get(key, default)

    def cache_clear(self):
        '''
        Clear class cache for current device.
        '''
        if self.device and self.cache and self.device.id in self.cache:
            del(self.cache[self.device.id])

        self.device = None


class XenServer(PythonPlugin, ModelerPluginCacheMixin):
    deviceProperties = PythonPlugin.deviceProperties + (
        'xenserver_addresses',
        'zXenServerUsername',
        'zXenServerPassword',
        )

    @inlineCallbacks
    def collect(self, device, unused):
        '''
        Asynchronously collect data from device. Return a deferred.
        '''
        LOG.info("Collecting data for device %s", device.id)

        if not device.xenserver_addresses:
            LOG.warn("zXenServerAddresses not set. Modeling aborted")
            returnValue(None)

        if not device.zXenServerUsername:
            LOG.warn("zXenServerUsername not set. Modeling aborted")
            returnValue(None)

        if not device.zXenServerPassword:
            LOG.warn("zXenServerPassword not set. Modeling aborted")
            returnValue(None)

        client = txxenapi.Client(
            device.xenserver_addresses,
            device.zXenServerUsername,
            device.zXenServerPassword)

        # Simultaneously call client.xenapi.xxx.get_all_records() for
        # each XAPI class.
        results = yield DeferredList([
            getattr(client.xenapi, x).get_all_records() for x in XAPI_CLASSES])

        try:
            yield client.close()
        except Exception, ex:
            LOG.warn(
                "%s %s failed to logout: %s",
                self.device, self.name(), ex)

        returnValue(results)

    def process(self, device, results, unused):
        '''
        Process results of collect method.

        results is a list of two element tuples where the first element
        is a boolean indicating whether the call was successful or not,
        and the second element is a dictionary keyed by object OpaqueRef
        with a dictionary of properties as the value.

            [
                (success, {'OpaqueRef:xxx-xxx': {...}}),
                (success, {'OpaqueRef:xxx-xxx': {...}}),
            ]

        The list indexes map to the the indexes of XAPI_CLASSES.
        '''
        if results is None:
            return None

        # Check to see if all requests failed.
        if set((x[0], x[1] is not None) for x in results) == [(False, False)]:
            LOG.error("No XenServer API response from %s", device.id)
            return None

        LOG.info("Processing data for device %s", device.id)

        self.cache_prepare(device)

        maps = []

        # Call self.xxx_relmaps(self, respective_results) for each XAPI
        # class.
        for i, xapi_class in enumerate(XAPI_CLASSES):
            if not results[i][0] or results[i][1] is None:
                LOG.error(
                    "No XenServer API response for %s from %s",
                    xapi_class, device.id)

                continue

            maps.extend(
                getattr(self, '%s_relmaps' % xapi_class.lower())(
                    results[i][1]))

        # Pick up any other maps that can be built with data cached
        # during the main process loop above. This allows for modeling
        # object not represented 1-for-1 by XAPI_CLASSES.
        maps.extend(self.other_maps())

        self.cache_clear()

        return maps

    def sr_relmaps(self, results):
        '''
        Yield a single srs RelationshipMap.
        '''
        objmaps = []

        for ref, properties in results.items():
            title = properties.get('name_label') or properties['uuid']

            objmaps.append({
                'id': id_from_ref(ref),
                'title': title,
                'setPBDs': ids_from_refs(properties.get('PBDs', []))
                })

        yield RelationshipMap(
            relname='srs',
            modname=MODULE_NAME['SR'],
            objmaps=objmaps)

    def vdi_relmaps(self, results):
        '''
        Yield a vdis RelationshipMap for each storage repository.
        '''
        objmaps = collections.defaultdict(list)

        for ref, properties in results.items():
            title = properties.get('name_label') or \
                properties.get('location') or \
                properties['uuid']

            objmaps[properties['SR']].append({
                'id': id_from_ref(ref),
                'title': title,
                'setVBDs': ids_from_refs(properties.get('VBDs', [])),
                })

        for ref, ref_objmaps in objmaps.items():
            yield RelationshipMap(
                compname='srs/%s' % id_from_ref(ref),
                relname='vdis',
                modname=MODULE_NAME['VDI'],
                objmaps=ref_objmaps)

    def host_relmaps(self, results):
        '''
        Yield a single hosts RelationshipMap.
        '''

        # Cache API version information for use in other_maps.
        try:
            properties = results.itervalues().next()
        except StopIteration:
            # Who cares if there aren't any hosts?
            pass
        else:
            manufacturer = properties.get('API_version_vendor')
            version_major = properties.get('API_version_major')
            version_minor = properties.get('API_version_minor')

            if manufacturer and version_major and version_minor:
                model = 'XenAPI %s.%s' % (version_major, version_minor)

                self.cache_set('api', 'product', {
                    'manufacturer': manufacturer,
                    'model': model,
                    })

        # Create host ObjectMaps.
        host_oms = []

        for ref, properties in results.items():
            title = properties.get('name_label') or properties.get('hostname')

            host_oms.append({
                'id': id_from_ref(ref),
                'title': title,
                'name_label': properties.get('name_label'),
                'name_description': properties.get('name_description'),
                'address': properties.get('address'),
                'setVMs': ids_from_refs(properties.get('resident_VMs', [])),
                'setSuspendImageSR': id_from_ref(properties.get('suspend_image_sr')),
                'setCrashDumpSR': id_from_ref(properties.get('crash_dump_sr')),
                'setLocalCacheSR': id_from_ref(properties.get('local_cache_sr')),
                })

            # To be used as a default for containing pool with no name.
            self.cache_set('host_titles', ref, title)

        yield RelationshipMap(
            relname='hosts',
            modname=MODULE_NAME['Host'],
            objmaps=host_oms)

    def host_cpu_relmaps(self, results):
        '''
        Yield a hostcpus RelationshipMap for each host.
        '''
        objmaps = collections.defaultdict(list)

        for ref, properties in results.items():
            title = properties.get('number') or properties['uuid']

            objmaps[properties['host']].append({
                'id': id_from_ref(ref),
                'title': title,
                })

        for parent_ref, grouped_objmaps in objmaps.items():
            yield RelationshipMap(
                compname='hosts/%s' % id_from_ref(parent_ref),
                relname='hostcpus',
                modname=MODULE_NAME['HostCPU'],
                objmaps=grouped_objmaps)

    def pbd_relmaps(self, results):
        '''
        Yield a pbds RelationshipMap for each host.
        '''
        objmaps = collections.defaultdict(list)

        for ref, properties in results.items():
            device_config = properties['device_config']

            title = device_config.get('location') or \
                device_config.get('device') or \
                properties['uuid']

            objmaps[properties['host']].append({
                'id': id_from_ref(ref),
                'title': title,
                'setSR': id_from_ref(properties.get('SR')),
                })

        for parent_ref, grouped_objmaps in objmaps.items():
            yield RelationshipMap(
                compname='hosts/%s' % id_from_ref(parent_ref),
                relname='pbds',
                modname=MODULE_NAME['PBD'],
                objmaps=grouped_objmaps)

    def pif_relmaps(self, results):
        '''
        Yield a pifs RelationshipMap for each host.
        '''
        objmaps = collections.defaultdict(list)

        for ref, properties in results.items():
            title = properties.get('device') or properties['uuid']

            objmaps[properties['host']].append({
                'id': id_from_ref(ref),
                'title': title,
                'setNetwork': id_from_ref(properties.get('network')),
                })

        for parent_ref, grouped_objmaps in objmaps.items():
            yield RelationshipMap(
                compname='hosts/%s' % id_from_ref(parent_ref),
                relname='pifs',
                modname=MODULE_NAME['PIF'],
                objmaps=grouped_objmaps)

    def network_relmaps(self, results):
        '''
        Yield a single networks RelationshipMap.
        '''
        objmaps = []

        for ref, properties in results.items():
            title = properties.get('name_label') or properties['uuid']

            objmaps.append({
                'id': id_from_ref(ref),
                'title': title,
                'setPIFs': ids_from_refs(properties.get('PIFs', [])),
                'setVIFs': ids_from_refs(properties.get('VIFs', [])),
                })

        yield RelationshipMap(
            relname='networks',
            modname=MODULE_NAME['Network'],
            objmaps=objmaps)

    def vm_relmaps(self, results):
        '''
        Yield a single vms RelationshipMap.
        '''
        objmaps = []

        for ref, properties in results.items():
            if properties.get('is_a_snapshot') or \
                    properties.get('is_snapshot_from_vmpp') or \
                    properties.get('is_a_template'):

                continue

            title = properties.get('name_label') or properties['uuid']

            objmaps.append({
                'id': id_from_ref(ref),
                'title': title,
                'setHost': id_from_ref(properties.get('resident_on')),
                'setVMAppliance': id_from_ref(properties.get('appliance')),
                })

        yield RelationshipMap(
            relname='vms',
            modname=MODULE_NAME['VM'],
            objmaps=objmaps)

    def vbd_relmaps(self, results):
        '''
        Yield a vbds RelationshipMap for each VM.
        '''
        objmaps = collections.defaultdict(list)

        for ref, properties in results.items():
            title = properties.get('device') or \
                properties.get('userdevice') or \
                properties['uuid']

            objmaps[properties['VM']].append({
                'id': id_from_ref(ref),
                'title': title,
                'setVDI': id_from_ref(properties.get('VDI')),
                })

        for parent_ref, grouped_objmaps in objmaps.items():
            yield RelationshipMap(
                compname='vms/%s' % id_from_ref(parent_ref),
                relname='vbds',
                modname=MODULE_NAME['VBD'],
                objmaps=grouped_objmaps)

    def vif_relmaps(self, results):
        '''
        Yield a vifs RelationshipMap for each VM.
        '''
        # TODO: Build objmaps.
        objmaps = collections.defaultdict(list)

        for ref, properties in results.items():
            title = properties.get('device') or properties['uuid']

            objmaps[properties['VM']].append({
                'id': id_from_ref(ref),
                'title': title,
                'setNetwork': id_from_ref(properties.get('network')),
                })

        for parent_ref, grouped_objmaps in objmaps.items():
            yield RelationshipMap(
                compname='vms/%s' % id_from_ref(parent_ref),
                relname='vifs',
                modname=MODULE_NAME['VIF'],
                objmaps=grouped_objmaps)

    def vm_appliance_relmaps(self, results):
        '''
        Yield a single vmappliances RelationshipMap.
        '''
        objmaps = []

        for ref, properties in results.items():
            title = properties.get('name_label') or properties['uuid']

            objmaps.append({
                'id': id_from_ref(ref),
                'title': title,
                'setVMs': ids_from_refs(properties.get('VMs', [])),
                })

        yield RelationshipMap(
            relname='vmappliances',
            modname=MODULE_NAME['VMAppliance'],
            objmaps=objmaps)

    def pool_relmaps(self, results):
        '''
        Yield a single pools RelationshipMap.
        '''
        objmaps = []

        for ref, properties in results.items():
            pool_title = properties.get('name_label')

            # By default pools will not have a name_label. XenCenter
            # shows the master host's name_label in this case. We should
            # do the same.
            if not pool_title:
                master_ref = properties.get('master')
                if master_ref:
                    pool_title = self.cache_get('host_titles', master_ref)

            objmaps.append({
                'id': id_from_ref(ref),
                'title': pool_title,
                'setMaster': id_from_ref(properties.get('master')),
                'setDefaultSR': id_from_ref(properties.get('default_SR')),
                'setSuspendImageSR': id_from_ref(properties.get('suspend_image_SR')),
                'setCrashDumpSR': id_from_ref(properties.get('crash_dump_SR')),
                })

        yield RelationshipMap(
            relname='pools',
            modname=MODULE_NAME['Pool'],
            objmaps=objmaps)

    def other_maps(self):
        '''
        Yield DataMaps that don't map directly to one of the
        XAPI_CLASSES through their respective *_relmaps methods.
        '''
        # This information is gathered from the host call. So it should
        # be cached in the host_relmaps method.
        api = self.cache_get('api', 'product')
        if api:
            yield ObjectMap(compname='os', data={
                'setProductKey': MultiArgs(api['model'], api['manufacturer']),
                })
