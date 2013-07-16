
######################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is
# installed.
#
######################################################################

from zope.interface import implements
from Products.ZenModel.ZenossSecurity import ZEN_CHANGE_DEVICE
from Products.Zuul.decorators import info
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.utils import ZuulMessageFactory as _t
from Products.ZenModel.DeviceComponent import DeviceComponent
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.Zuul.catalog.paths import DefaultPathReporter, relPath
from Products.Zuul.infos.component import ComponentInfo
from Products.Zuul.interfaces.component import IComponentInfo
from Products.ZenRelations.RelSchema import ToMany,ToManyCont,ToOne
from Products.ZenRelations.RelSchema import ToManyCont,ToOne
from ZenPacks.zenoss.XenServer.utils import updateToMany

class Network(DeviceComponent, ManagedEntity):
    meta_type = portal_type = 'XenServerNetwork'

    Klasses = [DeviceComponent, ManagedEntity]

    bridge = None
    uuid = None
    tags = None
    name_label = None
    MTU = None
    default_locking_mode = None
    name_description = None

    _properties = ()
    for Klass in Klasses:
        _properties = _properties + getattr(Klass,'_properties', ())

    _properties = _properties + (
        {'id': 'bridge', 'type': 'string', 'mode': 'w'},
        {'id': 'uuid', 'type': 'string', 'mode': 'w'},
        {'id': 'tags', 'type': 'string', 'mode': 'w'},
        {'id': 'name_label', 'type': 'string', 'mode': 'w'},
        {'id': 'MTU', 'type': 'string', 'mode': 'w'},
        {'id': 'default_locking_mode', 'type': 'string', 'mode': 'w'},
        {'id': 'name_description', 'type': 'string', 'mode': 'w'},
        )

    _relations = ()
    for Klass in Klasses:
        _relations = _relations + getattr(Klass, '_relations', ())

    _relations = _relations + (
        ('endpoint', ToOne(ToManyCont, 'ZenPacks.zenoss.XenServer.Endpoint', 'networks',)),
        ('pifs', ToMany(ToOne, 'ZenPacks.zenoss.XenServer.PIF', 'network',)),
        ('vifs', ToMany(ToOne, 'ZenPacks.zenoss.XenServer.VIF', 'network',)),
        )

    factory_type_information = ({
        'actions': ({
            'id': 'perfConf',
            'name': 'Template',
            'action': 'objTemplates',
            'permissions': (ZEN_CHANGE_DEVICE,),
            },),
        },)

    def device(self):
        '''
        Return device under which this component/device is contained.
        '''
        obj = self

        for i in range(200):
            if isinstance(obj, Device):
                return obj

            try:
                obj = obj.getPrimaryParent()
            except AttributeError as exc:
                raise AttributeError(
                    'Unable to determine parent at %s (%s) '
                    'while getting device for %s' % (
                        obj, exc, self))

    def getPIFIds(self):
        '''
        Return a sorted list of each pif id related to this
        Aggregate.

        Used by modeling.
        '''

        return sorted([pif.id for pif in self.pifs.objectValuesGen()])

    def setPIFIds(self, ids):
        '''
        Update PIF relationship given ids.

        Used by modeling.
        '''
        updateToMany(
            relationship=self.pifs,
            root=self.device(),
            type_=ZenPacks.zenoss.XenServer.PIF,
            ids=ids)

    def getVIFIds(self):
        '''
        Return a sorted list of each vif id related to this
        Aggregate.

        Used by modeling.
        '''

        return sorted([vif.id for vif in self.vifs.objectValuesGen()])

    def setVIFIds(self, ids):
        '''
        Update VIF relationship given ids.

        Used by modeling.
        '''
        updateToMany(
            relationship=self.vifs,
            root=self.device(),
            type_=ZenPacks.zenoss.XenServer.VIF,
            ids=ids)

class INetworkInfo(IComponentInfo):
    pif_count = schema.Int(title=_t(u'Number of PIFS'))
    vif_count = schema.Int(title=_t(u'Number of VIFS'))

    bridge = schema.TextLine(title=_t(u'bridges'))
    uuid = schema.TextLine(title=_t(u'uuids'))
    tags = schema.TextLine(title=_t(u'tag'))
    name_label = schema.TextLine(title=_t(u'name_labels'))
    MTU = schema.TextLine(title=_t(u'MTUS'))
    default_locking_mode = schema.TextLine(title=_t(u'default_locking_modes'))
    name_description = schema.TextLine(title=_t(u'name_descriptions'))

class NetworkInfo(ComponentInfo):
    implements(INetworkInfo)

    bridge = ProxyProperty('bridge')
    uuid = ProxyProperty('uuid')
    tags = ProxyProperty('tags')
    name_label = ProxyProperty('name_label')
    MTU = ProxyProperty('MTU')
    default_locking_mode = ProxyProperty('default_locking_mode')
    name_description = ProxyProperty('name_description')


    @property
    def pif_count():
        # Using countObjects is fast.
        try:
            return self._object.pifs.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.pifs())

    @property
    def vif_count():
        # Using countObjects is fast.
        try:
            return self._object.vifs.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.vifs())

