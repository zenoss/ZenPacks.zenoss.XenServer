
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

class SR(DeviceComponent, ManagedEntity):
    meta_type = portal_type = 'XenServerSR'

    Klasses = [DeviceComponent, ManagedEntity]

    uuid = None
    physical_size = None
    name_label = None
    physical_utilisation = None
    content_type = None
    shared = None
    name_description = None
    virtual_allocation = None

    _properties = ()
    for Klass in Klasses:
        _properties = _properties + getattr(Klass,'_properties', ())

    _properties = _properties + (
        {'id': 'uuid', 'type': 'string', 'mode': 'w'},
        {'id': 'physical_size', 'type': 'string', 'mode': 'w'},
        {'id': 'name_label', 'type': 'string', 'mode': 'w'},
        {'id': 'physical_utilisation', 'type': 'string', 'mode': 'w'},
        {'id': 'content_type', 'type': 'string', 'mode': 'w'},
        {'id': 'shared', 'type': 'string', 'mode': 'w'},
        {'id': 'name_description', 'type': 'string', 'mode': 'w'},
        {'id': 'virtual_allocation', 'type': 'string', 'mode': 'w'},
        )

    _relations = ()
    for Klass in Klasses:
        _relations = _relations + getattr(Klass, '_relations', ())

    _relations = _relations + (
        ('endpoint', ToOne(ToManyCont, 'ZenPacks.zenoss.XenServer.Endpoint', 'srs',)),
        ('pbds', ToMany(ToOne, 'ZenPacks.zenoss.XenServer.PBD', 'sr',)),
        ('vdis', ToManyCont(ToOne, 'ZenPacks.zenoss.XenServer.VDI', 'sr',)),
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

    def getPBDIds(self):
        '''
        Return a sorted list of each pbd id related to this
        Aggregate.

        Used by modeling.
        '''

        return sorted([pbd.id for pbd in self.pbds.objectValuesGen()])

    def setPBDIds(self, ids):
        '''
        Update PBD relationship given ids.

        Used by modeling.
        '''
        updateToMany(
            relationship=self.pbds,
            root=self.device(),
            type_=ZenPacks.zenoss.XenServer.PBD,
            ids=ids)

class ISRInfo(IComponentInfo):
    vdi_count = schema.Int(title=_t(u'Number of VDIS'))
    pbd_count = schema.Int(title=_t(u'Number of PBDS'))

    uuid = schema.TextLine(title=_t(u'uuids'))
    physical_size = schema.TextLine(title=_t(u'physical_sizes'))
    name_label = schema.TextLine(title=_t(u'name_labels'))
    physical_utilisation = schema.TextLine(title=_t(u'physical_utilisations'))
    content_type = schema.TextLine(title=_t(u'content_types'))
    shared = schema.TextLine(title=_t(u'shareds'))
    name_description = schema.TextLine(title=_t(u'name_descriptions'))
    virtual_allocation = schema.TextLine(title=_t(u'virtual_allocations'))

class SRInfo(ComponentInfo):
    implements(ISRInfo)

    uuid = ProxyProperty('uuid')
    physical_size = ProxyProperty('physical_size')
    name_label = ProxyProperty('name_label')
    physical_utilisation = ProxyProperty('physical_utilisation')
    content_type = ProxyProperty('content_type')
    shared = ProxyProperty('shared')
    name_description = ProxyProperty('name_description')
    virtual_allocation = ProxyProperty('virtual_allocation')


    @property
    def vdi_count():
        # Using countObjects is fast.
        try:
            return self._object.vdis.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.vdis())

    @property
    def pbd_count():
        # Using countObjects is fast.
        try:
            return self._object.pbds.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.pbds())

