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
from Products.ZenRelations.RelSchema import ToManyCont, ToOne
from Products.Zuul.form import schema
from Products.Zuul.infos.device import DeviceInfo
from Products.Zuul.interfaces import IDeviceInfo
from Products.Zuul.utils import ZuulMessageFactory as _t

from ZenPacks.zenoss.XenServer import MODULE_NAME
from ZenPacks.zenoss.XenServer.utils import RelationshipLengthProperty


class Endpoint(Device):
    meta_type = portal_type = 'Endpoint'

    _relations = Device._relations + (
        ('hosts', ToManyCont(ToOne, MODULE_NAME['Host'], 'endpoint')),
        ('networks', ToManyCont(ToOne, MODULE_NAME['Network'], 'endpoint')),
        ('pools', ToManyCont(ToOne, MODULE_NAME['Pool'], 'endpoint')),
        ('srs', ToManyCont(ToOne, MODULE_NAME['SR'], 'endpoint')),
        ('vmappliances', ToManyCont(ToOne, MODULE_NAME['VMAppliance'], 'endpoint')),
        ('vms', ToManyCont(ToOne, MODULE_NAME['VM'], 'endpoint')),
        )

    def xenserver_addresses(self):
        '''
        Return a list of all known XenServer host addresses.

        Prefer hostname discovered from the endpoint. Fall back to
        user-configured addresses that are less likely to be up to date.
        '''
        addresses = [x.hostname for x in self.hosts() if x.hostname]

        if not addresses:
            addresses = self.zXenServerAddresses

        return addresses


class IEndpointInfo(IDeviceInfo):
    '''
    API Info interface for Endpoint.
    '''

    pool_count = schema.Int(title=_t(u'Number of Pools'))
    host_count = schema.Int(title=_t(u'Number of Hosts'))
    sr_count = schema.Int(title=_t(u'Number of SRs'))
    network_count = schema.Int(title=_t(u'Number of Networks'))
    vm_count = schema.Int(title=_t(u'Number of VMs'))
    vmappliance_count = schema.Int(title=_t(u'Number of VM Appliances'))


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
