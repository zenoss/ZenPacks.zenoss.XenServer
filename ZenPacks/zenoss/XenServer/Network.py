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
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.utils import ZuulMessageFactory as _t

from ZenPacks.zenoss.XenServer import CLASS_NAME, MODULE_NAME
from ZenPacks.zenoss.XenServer.utils import (
    PooledComponent, IPooledComponentInfo, PooledComponentInfo,
    RelationshipLengthProperty,
    updateToMany,
    )


class Network(PooledComponent):
    '''
    Model class for Network.
    '''

    meta_type = portal_type = 'XenServerNetwork'

    mtu = None
    allowed_operations = None
    bridge = None
    default_locking_mode = None
    name_description = None
    name_label = None
    ipv4_begin = None
    ipv4_end = None
    is_guest_installer_network = None
    is_host_internal_management_network = None
    ipv4_netmask = None

    _properties = PooledComponent._properties + (
        {'id': 'mtu', 'type': 'string', 'mode': 'w'},
        {'id': 'allowed_operations', 'type': 'lines', 'mode': 'w'},
        {'id': 'bridge', 'type': 'string', 'mode': 'w'},
        {'id': 'default_locking_mode', 'type': 'string', 'mode': 'w'},
        {'id': 'name_description', 'type': 'string', 'mode': 'w'},
        {'id': 'name_label', 'type': 'string', 'mode': 'w'},
        {'id': 'ipv4_begin', 'type': 'string', 'mode': 'w'},
        {'id': 'ipv4_end', 'type': 'string', 'mode': 'w'},
        {'id': 'is_guest_installer_network', 'type': 'boolean', 'mode': 'w'},
        {'id': 'is_host_internal_management_network', 'type': 'boolean', 'mode': 'w'},
        {'id': 'ipv4_netmask', 'type': 'string', 'mode': 'w'},
        )

    _relations = PooledComponent._relations + (
        ('endpoint', ToOne(ToManyCont, MODULE_NAME['Endpoint'], 'networks')),
        ('pifs', ToMany(ToOne, MODULE_NAME['PIF'], 'network')),
        ('vifs', ToMany(ToOne, MODULE_NAME['VIF'], 'network')),
        )

    def getPIFs(self):
        '''
        Return a sorted list of ids in pifs relationship.

        Used by modeling.
        '''

        return sorted(pif.id for pif in self.pifs.objectValuesGen())

    def setPIFs(self, pif_ids):
        '''
        Update pifs relationship given ids.

        Used by modeling.
        '''
        updateToMany(
            relationship=self.pifs,
            root=self.device(),
            type_=CLASS_NAME['PIF'],
            ids=pif_ids)

    def getVIFs(self):
        '''
        Return a sorted list of ids in vifs relationship.

        Used by modeling.
        '''

        return sorted(vif.id for vif in self.vifs.objectValuesGen())

    def setVIFs(self, vif_ids):
        '''
        Update vifs relationship given ids.

        Used by modeling.
        '''
        updateToMany(
            relationship=self.vifs,
            root=self.device(),
            type_=CLASS_NAME['VIF'],
            ids=vif_ids)

    def xenrrd_prefix(self):
        '''
        Return prefix under which XenServer stores RRD data about this
        component.
        '''
        # This is a guess at future support. XenServer 6.2 doesn't have
        # any RRD data for networks.
        if self.xenapi_uuid:
            return ('network', self.xenapi_uuid, '')


class INetworkInfo(IPooledComponentInfo):
    '''
    API Info interface for Network.
    '''

    mtu = schema.TextLine(title=_t(u'MTU'))
    allowed_operations = schema.Text(title=_t(u'Allowed Operations'))
    bridge = schema.TextLine(title=_t(u'Bridge'))
    default_locking_mode = schema.TextLine(title=_t(u'Default Locking Mode'))
    name_description = schema.TextLine(title=_t(u'Description'))
    name_label = schema.TextLine(title=_t(u'Label'))
    ipv4_begin = schema.TextLine(title=_t(u'IPv4 Begin'))
    ipv4_end = schema.TextLine(title=_t(u'IPv4 End'))
    is_guest_installer_network = schema.Bool(title=_t(u'Guest Installer Network'))
    is_host_internal_management_network = schema.Bool(title=_t(u'Host Internal Management Network'))
    ipv4_netmask = schema.TextLine(title=_t(u'IPv4 Netmask'))

    pif_count = schema.Int(title=_t(u'Number of Physical Network Interfaces'))
    vif_count = schema.Int(title=_t(u'Number of Virtual Network Interfaces'))


class NetworkInfo(PooledComponentInfo):
    '''
    API Info adapter factory for Network.
    '''

    implements(INetworkInfo)
    adapts(Network)

    mtu = ProxyProperty('mtu')
    allowed_operations = ProxyProperty('allowed_operations')
    bridge = ProxyProperty('bridge')
    default_locking_mode = ProxyProperty('default_locking_mode')
    name_description = ProxyProperty('name_description')
    name_label = ProxyProperty('name_label')
    ipv4_begin = ProxyProperty('ipv4_begin')
    ipv4_end = ProxyProperty('ipv4_end')
    is_guest_installer_network = ProxyProperty('is_guest_installer_network')
    is_host_internal_management_network = ProxyProperty('is_host_internal_management_network')
    ipv4_netmask = ProxyProperty('ipv4_netmask')

    pif_count = RelationshipLengthProperty('pifs')
    vif_count = RelationshipLengthProperty('vifs')
