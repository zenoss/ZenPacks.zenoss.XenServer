######################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is
# installed.
#
######################################################################

from zope.component import adapts
from zope.interface import implements

from Products.ZenModel.Device import Device
from Products.ZenModel.ZenossSecurity import ZEN_VIEW
from Products.ZenRelations.RelSchema import ToManyCont, ToOne
from Products.Zuul import getFacade
from Products.Zuul.form import schema
from Products.Zuul.infos.device import DeviceInfo
from Products.Zuul.interfaces import IDeviceInfo
from Products.Zuul.utils import ZuulMessageFactory as _t

from ZenPacks.zenoss.XenServer import MODULE_NAME
from ZenPacks.zenoss.XenServer.utils import RelationshipLengthProperty


class Endpoint(Device):
    '''
    Model class for Endpoint.
    '''

    class_label = 'Endpoint'
    class_plural_label = 'Endpoints'

    meta_type = portal_type = 'XenServerEndpoint'

    _relations = Device._relations + (
        ('hosts', ToManyCont(ToOne, MODULE_NAME['Host'], 'endpoint')),
        ('networks', ToManyCont(ToOne, MODULE_NAME['Network'], 'endpoint')),
        ('pools', ToManyCont(ToOne, MODULE_NAME['Pool'], 'endpoint')),
        ('srs', ToManyCont(ToOne, MODULE_NAME['SR'], 'endpoint')),
        ('vmappliances', ToManyCont(ToOne, MODULE_NAME['VMAppliance'], 'endpoint')),
        ('vms', ToManyCont(ToOne, MODULE_NAME['VM'], 'endpoint')),
        )

    factory_type_information = ({
        'actions': ({
            'id': 'events',
            'name': 'Events',
            'action': 'viewEvents',
            'permissions': (ZEN_VIEW,),
            },),
        },)

    @property
    def xenserver_addresses(self):
        '''
        Return a list of all known XenServer host addresses.

        Prefer hostname discovered from the endpoint. Fall back to
        user-configured addresses that are less likely to be up to date.
        '''
        addresses = [x.address for x in self.hosts() if x.address]

        if not addresses:
            addresses = self.zXenServerAddresses

        return addresses

    @property
    def open_message_clear_tuples(self):
        '''
        Return set of tuples for open XenServerMessage events.

        Used by the collector to send clear events when messages have
        been dismissed on the XenServer or in XenCenter.
        '''
        zep = getFacade('zep')
        event_filter = zep.createEventFilter(
            status=(0, 1, 2),
            severity=(1, 2, 3, 4, 5),
            event_class_key='XenServerMessage',
            agent='zenpython',)

        clear_tuples = set()

        summaries = zep.getEventSummariesGenerator(filter=event_filter)
        for summary in summaries:
            for occurrence in summary.get('occurrence', []):
                actor = occurrence.get('actor')
                if not actor:
                    continue

                device = actor.get('element_identifier', '')

                component = None
                for detail in occurrence.get('details', []):
                    if detail.get('name') == 'xenserver_obj_uuid':
                        component = detail.get('value', [''])[0]

                eventKey = occurrence.get('event_key', '')

                clear_tuple = (device, component, eventKey)
                if all(clear_tuple):
                    clear_tuples.add(clear_tuple)

        return clear_tuples

    def getIconPath(self):
        '''
        Return URL to icon representing objects of this class.
        '''
        return '/++resource++xenserver/img/xenserver.png'


class IEndpointInfo(IDeviceInfo):
    '''
    API Info interface for Endpoint.
    '''

    pool_count = schema.Int(title=_t(u'Number of Pools'))
    host_count = schema.Int(title=_t(u'Number of Hosts'))
    sr_count = schema.Int(title=_t(u'Number of Storage Repositories'))
    network_count = schema.Int(title=_t(u'Number of Networks'))
    vm_count = schema.Int(title=_t(u'Number of VMs'))
    vmappliance_count = schema.Int(title=_t(u'Number of vApps'))


class EndpointInfo(DeviceInfo):
    '''
    API Info adapter factory for Datacenter.
    '''

    implements(IEndpointInfo)
    adapts(Endpoint)

    pool_count = RelationshipLengthProperty('pools')
    host_count = RelationshipLengthProperty('hosts')
    sr_count = RelationshipLengthProperty('srs')
    network_count = RelationshipLengthProperty('networks')
    vm_count = RelationshipLengthProperty('vms')
    vmappliance_count = RelationshipLengthProperty('vmappliances')
