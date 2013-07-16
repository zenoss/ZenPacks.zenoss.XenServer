
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
from ZenPacks.zenoss.XenServer.utils import updateToOne

class PBD(DeviceComponent, ManagedEntity):
    meta_type = portal_type = 'XenServerPBD'

    Klasses = [DeviceComponent, ManagedEntity]

    dc_legacy_mode = None
    current_attached = None
    dc_location = None
    uuid = None
    dc_device = None

    _properties = ()
    for Klass in Klasses:
        _properties = _properties + getattr(Klass,'_properties', ())

    _properties = _properties + (
        {'id': 'dc_legacy_mode', 'type': 'bool', 'mode': 'w'},
        {'id': 'current_attached', 'type': 'bool', 'mode': 'w'},
        {'id': 'dc_location', 'type': 'string', 'mode': 'w'},
        {'id': 'uuid', 'type': 'string', 'mode': 'w'},
        {'id': 'dc_device', 'type': 'string', 'mode': 'w'},
        )

    _relations = ()
    for Klass in Klasses:
        _relations = _relations + getattr(Klass, '_relations', ())

    _relations = _relations + (
        ('endpoint', ToOne(ToManyCont, 'ZenPacks.zenoss.XenServer.Endpoint', 'pbds',)),
        ('host', ToOne(ToManyCont, 'ZenPacks.zenoss.XenServer.Host', 'pbds',)),
        ('sr', ToOne(ToMany, 'ZenPacks.zenoss.XenServer.SR', 'pbds',)),
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

    def getsrId(self):
        '''
        Return sr id or None.

        Used by modeling.
        '''
        obj = self.sr()
        if obj: 
            return obj.id

    def setsrId(self, id_):
        '''
        Set sr by id.

        Used by modeling.
        '''
        updateToOne(
            relationship=self.sr,
            root=self.device(),
            type_=ZenPacks.zenoss.XenServer.SR,
            id_=id_)

class IPBDInfo(IComponentInfo):

    dc_legacy_mode = schema.Bool(title=_t(u'dc_legacy_modes'))
    current_attached = schema.Bool(title=_t(u'current_attacheds'))
    dc_location = schema.TextLine(title=_t(u'dc_locations'))
    uuid = schema.TextLine(title=_t(u'uuids'))
    dc_device = schema.TextLine(title=_t(u'dc_devices'))

class PBDInfo(ComponentInfo):
    implements(IPBDInfo)

    dc_legacy_mode = ProxyProperty('dc_legacy_mode')
    current_attached = ProxyProperty('current_attached')
    dc_location = ProxyProperty('dc_location')
    uuid = ProxyProperty('uuid')
    dc_device = ProxyProperty('dc_device')

class PBDPathReporter(DefaultPathReporter):
    def getPaths(self):
        paths = super(PBDPathReporter, self).getPaths()

        obj = self.context.sr()
        if obj:
            paths.extend(relPath(obj,'endpoint'))

        return paths
