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
from Products.ZenModel.Device import Device
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
from Products.ZenRelations.RelSchema import ToMany, ToManyCont, ToOne
from ZenPacks.zenoss.XenServer.utils import updateToOne


class VBD(DeviceComponent, ManagedEntity):
    meta_type = portal_type = 'XenServerVBD'

    Klasses = [DeviceComponent, ManagedEntity]

    uuid = None
    bootable = None
    status_code = None
    status_detail = None
    current_attached = None
    Type = None
    empty = None

    _properties = ()
    for Klass in Klasses:
        _properties = _properties + getattr(Klass, '_properties', ())

    _properties = _properties + (
        {'id': 'uuid', 'type': 'string', 'mode': 'w'},
        {'id': 'bootable', 'type': 'string', 'mode': 'w'},
        {'id': 'status_code', 'type': 'string', 'mode': 'w'},
        {'id': 'status_detail', 'type': 'string', 'mode': 'w'},
        {'id': 'current_attached', 'type': 'string', 'mode': 'w'},
        {'id': 'Type', 'type': 'string', 'mode': 'w'},
        {'id': 'empty', 'type': 'string', 'mode': 'w'},
        )

    _relations = ()
    for Klass in Klasses:
        _relations = _relations + getattr(Klass, '_relations', ())

    _relations = _relations + (
        ('vdi', ToOne(ToMany, 'ZenPacks.zenoss.XenServer.VDI', 'vbds',)),
        ('vm', ToOne(ToManyCont, 'ZenPacks.zenoss.XenServer.VM', 'vbds',)),
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

    def getvdiId(self):
        '''
        Return vdi id or None.

        Used by modeling.
        '''
        obj = self.vdi()
        if obj:
            return obj.id

    def setvdiId(self, id_):
        '''
        Set vdi by id.

        Used by modeling.
        '''
        updateToOne(
            relationship=self.vdi,
            root=self.device(),
            type_='ZenPacks.zenoss.XenServer.VDI',
            id_=id_)


class IVBDInfo(IComponentInfo):

    uuid = schema.TextLine(title=_t(u'uuids'))
    bootable = schema.TextLine(title=_t(u'bootables'))
    status_code = schema.TextLine(title=_t(u'status_codes'))
    status_detail = schema.TextLine(title=_t(u'status_details'))
    current_attached = schema.TextLine(title=_t(u'current_attacheds'))
    Type = schema.TextLine(title=_t(u'Types'))
    empty = schema.TextLine(title=_t(u'empties'))


class VBDInfo(ComponentInfo):
    implements(IVBDInfo)

    uuid = ProxyProperty('uuid')
    bootable = ProxyProperty('bootable')
    status_code = ProxyProperty('status_code')
    status_detail = ProxyProperty('status_detail')
    current_attached = ProxyProperty('current_attached')
    Type = ProxyProperty('Type')
    empty = ProxyProperty('empty')


class VBDPathReporter(DefaultPathReporter):
    def getPaths(self):
        paths = super(VBDPathReporter, self).getPaths()

        obj = self.context.vdi()
        if obj:
            paths.extend(relPath(obj, 'endpoint'))

        return paths
