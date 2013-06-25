#LICENSE HEADER SAMPLE
from zope.interface import implements
from Products.ZenModel.ZenossSecurity import ZEN_CHANGE_DEVICE
from Products.Zuul.decorators import info
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.utils import ZuulMessageFactory as _t
from Products.ZenModel.DeviceComponent import DeviceComponent
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.Zuul.infos.component import ComponentInfo
from Products.Zuul.interfaces.component import IComponentInfo
from Products.ZenRelations.RelSchema import ToManyCont,ToOne

class SR(DeviceComponent, ManagedEntity):
    meta_type = portal_type = 'SR'

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
        ('device', ToOne(ToManyCont, 'Products.ZenModel.Device.Device', 'srs',)),
        ('vbds', ToManyCont(ToOne, 'ZenPacks.zenoss.XenServer.VBD', 'sr',)),
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

class ISRInfo(IComponentInfo):
    vbd_count = schema.Int(title=_t(u'Number of VBDS'))

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
    def vbd_count():
        # Using countObjects is fast.
        try:
            return self._object.vbds.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.vbds())

