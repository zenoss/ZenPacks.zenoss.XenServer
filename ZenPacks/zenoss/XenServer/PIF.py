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

    dns = None
    ipv4_addresses = None
    ipv6_addresses = None
    macaddress = None
    mtu = None
    vlan = None
    currently_attached = None
    pif_device = None
    disallow_unplug = None
    ipv4_gateway = None
    ipv4_configuration_mode = None
    ipv6_configuration_mode = None
    ipv6_gateway = None
    management = None
    metrics = None
    ipv4_netmask = None
    physical = None
    primary_address_type = None

    _properties = PooledComponent._properties + (
        {'id': 'dns', 'type': 'string', 'mode': 'w'},
        {'id': 'ipv4_addresses', 'type': 'lines', 'mode': 'w'},
        {'id': 'ipv6_addresses', 'type': 'lines', 'mode': 'w'},
        {'id': 'macaddress', 'type': 'string', 'mode': 'w'},
        {'id': 'mtu', 'type': 'string', 'mode': 'w'},
        {'id': 'vlan', 'type': 'string', 'mode': 'w'},
        {'id': 'currently_attached', 'type': 'bool', 'mode': 'w'},
        {'id': 'pif_device', 'type': 'string', 'mode': 'w'},
        {'id': 'disallow_unplug', 'type': 'bool', 'mode': 'w'},
        {'id': 'ipv4_gateway', 'type': 'string', 'mode': 'w'},
        {'id': 'ipv4_configuration_mode', 'type': 'string', 'mode': 'w'},
        {'id': 'ipv6_configuration_mode', 'type': 'string', 'mode': 'w'},
        {'id': 'ipv6_gateway', 'type': 'string', 'mode': 'w'},
        {'id': 'management', 'type': 'bool', 'mode': 'w'},
        {'id': 'metrics', 'type': 'string', 'mode': 'w'},
        {'id': 'ipv4_netmask', 'type': 'string', 'mode': 'w'},
        {'id': 'physical', 'type': 'bool', 'mode': 'w'},
        {'id': 'primary_address_type', 'type': 'string', 'mode': 'w'},
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
    currently_attached = schema.Bool(title=_t(u'Currently Attached'))
    pif_device = schema.TextLine(title=_t(u'Network Device'))
    disallow_unplug = schema.Bool(title=_t(u'Disallow Unplug'))
    ipv4_gateway = schema.TextLine(title=_t(u'IPv4 Gateway'))
    ipv4_configuration_mode = schema.TextLine(title=_t(u'IPv4 Configuration Mode'))
    ipv6_configuration_mode = schema.TextLine(title=_t(u'IPv6 Configuration Mode'))
    ipv6_gateway = schema.TextLine(title=_t(u'IPv6 Gateway'))
    management = schema.Bool(title=_t(u'Management'))
    ipv4_netmask = schema.TextLine(title=_t(u'IPv4 Netmask'))
    physical = schema.Bool(title=_t(u'Physical'))
    primary_address_type = schema.TextLine(title=_t(u'Primary Address Type'))

    IP = schema.TextLine(title=_t(u'IPS'))
    MAC = schema.TextLine(title=_t(u'MACS'))
    netmask = schema.TextLine(title=_t(u'netmasks'))
    gateway = schema.TextLine(title=_t(u'gateways'))


class PIFInfo(PooledComponentInfo):
    '''
    API Info adapter factor for PIF.
    '''

    implements(IPIFInfo)
    adapts(PIF)

    host = RelationshipInfoProperty('host')
    network = RelationshipInfoProperty('network')

    dns = ProxyProperty('dns')
    ipv4_addresses = ProxyProperty('ipv4_addresses')
    ipv6_addresses = ProxyProperty('ipv6_addresses')
    macaddress = ProxyProperty('macaddress')
    mtu = ProxyProperty('mtu')
    vlan = ProxyProperty('vlan')
    currently_attached = ProxyProperty('currently_attached')
    pif_device = ProxyProperty('device')
    disallow_unplug = ProxyProperty('disallow_unplug')
    ipv4_gateway = ProxyProperty('ipv4_gateway')
    ipv4_configuration_mode = ProxyProperty('ipv4_configuration_mode')
    ipv6_configuration_mode = ProxyProperty('ipv6_configuration_mode')
    ipv6_gateway = ProxyProperty('ipv6_gateway')
    management = ProxyProperty('management')
    ipv4_netmask = ProxyProperty('ipv4_netmask')
    physical = ProxyProperty('physical')
    primary_address_type = ProxyProperty('primary_address_type')


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
