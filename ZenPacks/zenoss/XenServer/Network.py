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
    BaseComponent, IBaseComponentInfo, BaseComponentInfo,
    RelationshipLengthProperty,
    updateToMany,
    )


class Network(BaseComponent):
    '''
    Model class for Network.
    '''

    meta_type = portal_type = 'XenServerNetwork'

    name_label = None
    name_description = None
    bridge = None
    tags = None
    MTU = None
    default_locking_mode = None

    _properties = BaseComponent._properties + (
        {'id': 'name_label', 'type': 'string', 'mode': 'w'},
        {'id': 'name_description', 'type': 'string', 'mode': 'w'},
        {'id': 'bridge', 'type': 'string', 'mode': 'w'},
        {'id': 'tags', 'type': 'string', 'mode': 'w'},
        {'id': 'MTU', 'type': 'string', 'mode': 'w'},
        {'id': 'default_locking_mode', 'type': 'string', 'mode': 'w'},
        )

    _relations = BaseComponent._relations + (
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


class INetworkInfo(IBaseComponentInfo):
    '''
    API Info interface for Network.
    '''

    name_label = schema.TextLine(title=_t(u'name_labels'))
    name_description = schema.TextLine(title=_t(u'name_descriptions'))
    bridge = schema.TextLine(title=_t(u'bridges'))
    tags = schema.TextLine(title=_t(u'tag'))
    MTU = schema.TextLine(title=_t(u'MTUS'))
    default_locking_mode = schema.TextLine(title=_t(u'default_locking_modes'))

    pif_count = schema.Int(title=_t(u'Number of PIFS'))
    vif_count = schema.Int(title=_t(u'Number of VIFS'))


class NetworkInfo(BaseComponentInfo):
    '''
    API Info adapter factory for Network.
    '''

    implements(INetworkInfo)
    adapts(Network)

    name_label = ProxyProperty('name_label')
    name_description = ProxyProperty('name_description')
    bridge = ProxyProperty('bridge')
    tags = ProxyProperty('tags')
    MTU = ProxyProperty('MTU')
    default_locking_mode = ProxyProperty('default_locking_mode')

    pif_count = RelationshipLengthProperty('pifs')
    vif_count = RelationshipLengthProperty('vifs')
