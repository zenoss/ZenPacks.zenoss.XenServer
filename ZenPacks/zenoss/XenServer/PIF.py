######################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is
# installed.
#
######################################################################

import logging
LOG = logging.getLogger('zen.XenServer')

from zope.component import adapts
from zope.interface import implements

from Products.ZenRelations.RelSchema import ToMany, ToManyCont, ToOne
from Products.ZenUtils.Utils import prepId
from Products.Zuul.catalog.paths import DefaultPathReporter, relPath
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.utils import ZuulMessageFactory as _t

from ZenPacks.zenoss.XenServer import CLASS_NAME, MODULE_NAME
from ZenPacks.zenoss.XenServer.utils import (
    PooledComponent, IPooledComponentInfo, PooledComponentInfo,
    RelationshipInfoProperty,
    updateToOne,
    id_from_ref, int_or_none,
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

    _catalogs = dict({
        'PIFCatalog': {
            'deviceclass': '/XenServer',
            'indexes': {
                'ipv4_addresses': {'type': 'keyword'},
                'mac_addresses': {'type': 'keyword'},
                },
            },
        }, **PooledComponent._catalogs)

    @property
    def mac_addresses(self):
        return (self.macaddress,)

    @classmethod
    def objectmap(cls, ref, properties):
        '''
        Return an ObjectMap given XenAPI PIF ref and properties.
        '''
        if 'uuid' not in properties:
            return {
                'compname': 'hosts/{}'.format(id_from_ref(properties['parent'])),
                'relname': 'pifs',
                'id': id_from_ref(ref),
                }

        title = properties.get('device') or properties['uuid']

        # IP is a single string whereas IPv6 is a list.
        ipv4_addresses = [x for x in [properties.get('IP')] if x]
        ipv6_addresses = [x for x in properties.get('IPv6', []) if x]

        vlan = properties.get('VLAN')
        if vlan == '-1':
            vlan = None

        return {
            'compname': 'hosts/{}'.format(id_from_ref(properties.get('host'))),
            'relname': 'pifs',
            'id': id_from_ref(ref),
            'title': title,
            'xenapi_ref': ref,
            'xenapi_metrics_ref': properties.get('metrics'),
            'xenapi_uuid': properties.get('uuid'),
            'dns': properties.get('dns'),
            'ipv4_addresses': ipv4_addresses,
            'ipv6_addresses': ipv6_addresses,
            'macaddress': properties.get('MAC'),
            'mtu': properties.get('MTU'),
            'vlan': vlan,
            'currently_attached': properties.get('currently_attached'),
            'pif_device': properties.get('device'),
            'disallow_unplug': properties.get('disallow_unplug'),
            'ipv4_gateway': properties.get('gateway'),
            'ipv4_configuration_mode': properties.get('ip_configuration_mode'),
            'ipv6_configuration_mode': properties.get('ipv6_configuration_mode'),
            'ipv6_gateway': properties.get('ipv6_gateway'),
            'management': properties.get('management'),
            'ipv4_netmask': properties.get('netmask'),
            'physical': properties.get('physical'),
            'primary_address_type': properties.get('primary_address_type'),
            'setNetwork': id_from_ref(properties.get('network')),
            }

    @classmethod
    def objectmap_metrics(cls, ref, properties):
        '''
        Return an ObjectMap given XenAPI host ref and host_metrics
        properties.
        '''

        # Extract nested refs.
        ref, host_ref = ref

        speed = int_or_none(properties.get('speed'))
        if speed:
            speed = speed * 1e6  # Convert from Mbps to bps.

        return {
            'compname': 'hosts/{}'.format(id_from_ref(host_ref)),
            'relname': 'pifs',
            'id': id_from_ref(ref),
            'carrier': properties.get('carrier'),
            'pif_device_id': properties.get('device_id'),
            'pif_device_name': properties.get('device_name'),
            'speed': speed,
            'vendor_name': properties.get('vendor_name'),
            }

    @classmethod
    def findByMAC(cls, dmd, mac_addresses):
        '''
        Return the first PIF matching one of mac_addresses.
        '''
        return next(cls.search(
            dmd, 'PIFCatalog', mac_addresses=mac_addresses), None)

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

    def getIconPath(self):
        '''
        Return URL to icon representing objects of this class.
        '''
        return '/++resource++xenserver/img/virtual-network-interface.png'

    def server_interface(self):
        '''
        Return the server interface underlying this PIF.

        The host on which this PIF resides may also be monitored as a
        normal Linux server. Attempt to find that server and its
        interface that's associated with this PIF.
        '''
        if not self.pif_device:
            return

        server_device = self.host().server_device()
        if server_device:
            return server_device.os.interfaces._getOb(
                prepId(self.pif_device), None)


class IPIFInfo(IPooledComponentInfo):
    '''
    API Info interface for PIF.
    '''

    host = schema.Entity(title=_t(u'Host'))
    network = schema.Entity(title=_t(u'Network'))
    server_interface = schema.Entity(title=_t(u'Server Interface'))

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
    server_interface = RelationshipInfoProperty('server_interface')

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
