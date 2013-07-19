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
from ZenPacks.zenoss.XenServer.utils import updateToMany


class VDI(DeviceComponent, ManagedEntity):
    meta_type = portal_type = 'XenServerVDI'

    Klasses = [DeviceComponent, ManagedEntity]

    read_only = None
    sharable = None
    uuid = None
    missing = None
    name_label = None
    physical_utilisation = None
    allow_caching = None
    on_boot = None
    name_description = None
    virtual_size = None
    Type = None

    _properties = ()
    for Klass in Klasses:
        _properties = _properties + getattr(Klass, '_properties', ())

    _properties = _properties + (
        {'id': 'read_only', 'type': 'string', 'mode': 'w'},
        {'id': 'sharable', 'type': 'string', 'mode': 'w'},
        {'id': 'uuid', 'type': 'string', 'mode': 'w'},
        {'id': 'missing', 'type': 'string', 'mode': 'w'},
        {'id': 'name_label', 'type': 'string', 'mode': 'w'},
        {'id': 'physical_utilisation', 'type': 'string', 'mode': 'w'},
        {'id': 'allow_caching', 'type': 'string', 'mode': 'w'},
        {'id': 'on_boot', 'type': 'string', 'mode': 'w'},
        {'id': 'name_description', 'type': 'string', 'mode': 'w'},
        {'id': 'virtual_size', 'type': 'string', 'mode': 'w'},
        {'id': 'Type', 'type': 'string', 'mode': 'w'},
        )

    _relations = ()
    for Klass in Klasses:
        _relations = _relations + getattr(Klass, '_relations', ())

    _relations = _relations + (
        ('sr', ToOne(ToManyCont, 'ZenPacks.zenoss.XenServer.SR', 'vdis',)),
        ('vbds', ToMany(ToOne, 'ZenPacks.zenoss.XenServer.VBD', 'vdi',)),
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

    def getVBDIds(self):
        '''
        Return a sorted list of each vbd id related to this
        Aggregate.

        Used by modeling.
        '''

        return sorted([vbd.id for vbd in self.vbds.objectValuesGen()])

    def setVBDIds(self, ids):
        '''
        Update VBD relationship given ids.

        Used by modeling.
        '''
        updateToMany(
            relationship=self.vbds,
            root=self.device(),
            type_='ZenPacks.zenoss.XenServer.VBD',
            ids=ids)


class IVDIInfo(IComponentInfo):
    vbd_count = schema.Int(title=_t(u'Number of VBDS'))

    read_only = schema.TextLine(title=_t(u'read_onlies'))
    sharable = schema.TextLine(title=_t(u'sharables'))
    uuid = schema.TextLine(title=_t(u'uuids'))
    missing = schema.TextLine(title=_t(u'missings'))
    name_label = schema.TextLine(title=_t(u'name_labels'))
    physical_utilisation = schema.TextLine(title=_t(u'physical_utilisations'))
    allow_caching = schema.TextLine(title=_t(u'allow_cachings'))
    on_boot = schema.TextLine(title=_t(u'on_boots'))
    name_description = schema.TextLine(title=_t(u'name_descriptions'))
    virtual_size = schema.TextLine(title=_t(u'virtual_sizes'))
    Type = schema.TextLine(title=_t(u'Types'))


class VDIInfo(ComponentInfo):
    implements(IVDIInfo)

    read_only = ProxyProperty('read_only')
    sharable = ProxyProperty('sharable')
    uuid = ProxyProperty('uuid')
    missing = ProxyProperty('missing')
    name_label = ProxyProperty('name_label')
    physical_utilisation = ProxyProperty('physical_utilisation')
    allow_caching = ProxyProperty('allow_caching')
    on_boot = ProxyProperty('on_boot')
    name_description = ProxyProperty('name_description')
    virtual_size = ProxyProperty('virtual_size')
    Type = ProxyProperty('Type')

    @property
    def vbd_count(self):
        # Using countObjects is fast.
        try:
            return self._object.vbds.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.vbds())
