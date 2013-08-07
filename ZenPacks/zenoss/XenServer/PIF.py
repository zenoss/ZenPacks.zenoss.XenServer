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

from Products.ZenRelations.RelSchema import ToMany, ToManyCont, ToOne
from Products.Zuul.catalog.paths import DefaultPathReporter, relPath
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.utils import ZuulMessageFactory as _t

from ZenPacks.zenoss.XenServer import CLASS_NAME, MODULE_NAME
from ZenPacks.zenoss.XenServer.utils import (
    PooledComponent, IPooledComponentInfo, PooledComponentInfo,
    RelationshipInfoProperty,
    updateToOne,
    )


class PIF(PooledComponent):
    '''
    Model class for PIF (physical interface.)
    '''
    meta_type = portal_type = 'XenServerPIF'

    xenapi_metrics_ref = None
    dns = None
    ipv4_addresses = None
    ipv6_addresses = None
    macaddress = None
    mtu = None
    vlan = None
    carrier = None
    currently_attached = None
    pif_device = None
    pif_device_id = None
    disallow_unplug = None
    ipv4_gateway = None
    ipv4_configuration_mode = None
    ipv6_configuration_mode = None
    ipv6_gateway = None
    management = None
    pif_device_name = None
    ipv4_netmask = None
    physical = None
    primary_address_type = None
    speed = None
    vendor_name = None

    _properties = PooledComponent._properties + (
        {'id': 'xenapi_metrics_ref', 'type': 'string', 'mode': 'w'},
        {'id': 'dns', 'type': 'string', 'mode': 'w'},
        {'id': 'ipv4_addresses', 'type': 'lines', 'mode': 'w'},
        {'id': 'ipv6_addresses', 'type': 'lines', 'mode': 'w'},
        {'id': 'macaddress', 'type': 'string', 'mode': 'w'},
        {'id': 'mtu', 'type': 'string', 'mode': 'w'},
        {'id': 'vlan', 'type': 'string', 'mode': 'w'},
        {'id': 'carrier', 'type': 'boolean', 'mode': 'w'},
        {'id': 'currently_attached', 'type': 'boolean', 'mode': 'w'},
        {'id': 'pif_device', 'type': 'string', 'mode': 'w'},
        {'id': 'pif_device_id', 'type': 'string', 'mode': 'w'},
        {'id': 'pif_device_name', 'type': 'string', 'mode': 'w'},
        {'id': 'disallow_unplug', 'type': 'boolean', 'mode': 'w'},
        {'id': 'ipv4_gateway', 'type': 'string', 'mode': 'w'},
        {'id': 'ipv4_configuration_mode', 'type': 'string', 'mode': 'w'},
        {'id': 'ipv6_configuration_mode', 'type': 'string', 'mode': 'w'},
        {'id': 'ipv6_gateway', 'type': 'string', 'mode': 'w'},
        {'id': 'management', 'type': 'boolean', 'mode': 'w'},
        {'id': 'ipv4_netmask', 'type': 'string', 'mode': 'w'},
        {'id': 'physical', 'type': 'boolean', 'mode': 'w'},
        {'id': 'primary_address_type', 'type': 'string', 'mode': 'w'},
        {'id': 'speed', 'type': 'int', 'mode': 'w'},
        {'id': 'vendor_name', 'type': 'string', 'mode': 'w'},
        )

    _relations = PooledComponent._relations + (
        ('host', ToOne(ToManyCont, MODULE_NAME['Host'], 'pifs')),
        ('network', ToOne(ToMany, MODULE_NAME['Network'], 'pifs')),
        )

    def getNetwork(self):
        '''
        Return network id or None.

        Used by modeling.
        '''
        network = self.network()
        if network:
            return network.id

    def setNetwork(self, network_id):
        '''
        Set network by id.

        Used by modeling.
        '''
        updateToOne(
            relationship=self.network,
            root=self.device(),
            type_=CLASS_NAME['Network'],
            id_=network_id)

    def xenrrd_prefix(self):
        '''
        Return prefix under which XenServer stores RRD data about this
        component.
        '''
        host_uuid = self.host().xenapi_uuid
        if host_uuid and self.pif_device:
            return ('host', host_uuid, '_'.join(('pif', self.pif_device)))


class IPIFInfo(IPooledComponentInfo):
    '''
    API Info interface for PIF.
    '''

    host = schema.Entity(title=_t(u'Host'))
    network = schema.Entity(title=_t(u'Network'))

    dns = schema.TextLine(title=_t(u'DNS Server Address'))
    ipv4_addresses = schema.TextLine(title=_t(u'IPv4 Addresses'))
    ipv6_addresses = schema.TextLine(title=_t(u'IPv6 Addresses'))
    macaddress = schema.TextLine(title=_t(u'MAC Address'))
    mtu = schema.TextLine(title=_t(u'MTU'))
    vlan = schema.TextLine(title=_t(u'VLAN'))
    carrier = schema.Bool(title=_t(u'Carrier'))
    currently_attached = schema.Bool(title=_t(u'Currently Attached'))
    pif_device = schema.TextLine(title=_t(u'Network Device'))
    pif_device_id = schema.TextLine(title=_t(u'Network Device ID'))
    pif_device_name = schema.TextLine(title=_t(u'Network Device Name'))
    disallow_unplug = schema.Bool(title=_t(u'Disallow Unplug'))
    ipv4_gateway = schema.TextLine(title=_t(u'IPv4 Gateway'))
    ipv4_configuration_mode = schema.TextLine(title=_t(u'IPv4 Configuration Mode'))
    ipv6_configuration_mode = schema.TextLine(title=_t(u'IPv6 Configuration Mode'))
    ipv6_gateway = schema.TextLine(title=_t(u'IPv6 Gateway'))
    management = schema.Bool(title=_t(u'Management'))
    ipv4_netmask = schema.TextLine(title=_t(u'IPv4 Netmask'))
    physical = schema.Bool(title=_t(u'Physical'))
    primary_address_type = schema.TextLine(title=_t(u'Primary Address Type'))
    speed = schema.Int(title=_t(u'Speed'))
    vendor_name = schema.TextLine(title=_t(u'Vendor Name'))


class PIFInfo(PooledComponentInfo):
    '''
    API Info adapter factor for PIF.
    '''

    implements(IPIFInfo)
    adapts(PIF)

    host = RelationshipInfoProperty('host')
    network = RelationshipInfoProperty('network')

    xenapi_metrics_ref = ProxyProperty('xenapi_metrics_ref')
    dns = ProxyProperty('dns')
    ipv4_addresses = ProxyProperty('ipv4_addresses')
    ipv6_addresses = ProxyProperty('ipv6_addresses')
    macaddress = ProxyProperty('macaddress')
    mtu = ProxyProperty('mtu')
    vlan = ProxyProperty('vlan')
    carrier = ProxyProperty('carrier')
    currently_attached = ProxyProperty('currently_attached')
    pif_device = ProxyProperty('pif_device')
    pif_device_id = ProxyProperty('pif_device_id')
    pif_device_name = ProxyProperty('pif_device_name')
    disallow_unplug = ProxyProperty('disallow_unplug')
    ipv4_gateway = ProxyProperty('ipv4_gateway')
    ipv4_configuration_mode = ProxyProperty('ipv4_configuration_mode')
    ipv6_configuration_mode = ProxyProperty('ipv6_configuration_mode')
    ipv6_gateway = ProxyProperty('ipv6_gateway')
    management = ProxyProperty('management')
    ipv4_netmask = ProxyProperty('ipv4_netmask')
    physical = ProxyProperty('physical')
    primary_address_type = ProxyProperty('primary_address_type')
    speed = ProxyProperty('speed')
    vendor_name = ProxyProperty('vendor_name')


class PIFPathReporter(DefaultPathReporter):
    '''
    Path reporter for PIF.
    '''

    def getPaths(self):
        paths = super(PIFPathReporter, self).getPaths()

        network = self.context.network()
        if network:
            paths.extend(relPath(network, 'endpoint'))

        return paths
