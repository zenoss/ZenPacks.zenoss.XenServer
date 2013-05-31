#LICENSE HEADER SAMPLE
from zope.interface import implements
from Products.ZenModel.ZenossSecurity import ZEN_CHANGE_DEVICE
from Products.Zuul.decorators import info
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.utils import ZuulMessageFactory as _t
from Products.ZenModel.DeviceComponent import DeviceComponent
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.ZenRelations.RelSchema import ToManyCont,ToOne

class VM(DeviceComponent, ManagedEntity):
    meta_type = portal_type = 'VM'

    Klasses = [DeviceComponent, ManagedEntity]

    memory_static_min = None
    name_label = None
    uuid = None
    VCPUs_max = None
    memory_static_max = None
    VCPUs_at_startup = None
    memory_dynamic_max = None
    power_state = None
    name_description = None
    memory_dynamic_min = None
    memory_overhead = None

    for Klass in Klasses:
        _properties = _properties + getattr(Klass,'_properties', None)

    _properties = _properties + (
        {'id': 'memory_static_min', 'type': 'string', 'mode': 'w'},
        {'id': 'name_label', 'type': 'string', 'mode': 'w'},
        {'id': 'uuid', 'type': 'string', 'mode': 'w'},
        {'id': 'VCPUs_max', 'type': 'string', 'mode': 'w'},
        {'id': 'memory_static_max', 'type': 'string', 'mode': 'w'},
        {'id': 'VCPUs_at_startup', 'type': 'string', 'mode': 'w'},
        {'id': 'memory_dynamic_max', 'type': 'string', 'mode': 'w'},
        {'id': 'power_state', 'type': 'string', 'mode': 'w'},
        {'id': 'name_description', 'type': 'string', 'mode': 'w'},
        {'id': 'memory_dynamic_min', 'type': 'string', 'mode': 'w'},
        {'id': 'memory_overhead', 'type': 'string', 'mode': 'w'},
        )

    for Klass in Klasses:
        _relations = _relations + getattr(Klass, '_relations', None)

    _relations = _relations + (
        ('device', ToOne(ToManyCont, 'Products.ZenModel.Device.Device', 'vms',)),
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

class IVMInfo(IComponentInfo):

    memory_static_min = schema.TextLine(title=_t(u'memory_static_mins'))
    name_label = schema.TextLine(title=_t(u'name_labels'))
    uuid = schema.TextLine(title=_t(u'uuids'))
    VCPUs_max = schema.TextLine(title=_t(u'VCPUs_maxes'))
    memory_static_max = schema.TextLine(title=_t(u'memory_static_maxes'))
    VCPUs_at_startup = schema.TextLine(title=_t(u'VCPUs_at_startups'))
    memory_dynamic_max = schema.TextLine(title=_t(u'memory_dynamic_maxes'))
    power_state = schema.TextLine(title=_t(u'power_states'))
    name_description = schema.TextLine(title=_t(u'name_descriptions'))
    memory_dynamic_min = schema.TextLine(title=_t(u'memory_dynamic_mins'))
    memory_overhead = schema.TextLine(title=_t(u'memory_overheads'))

class VMInfo(ComponentInfo):
    implements(IVMInfo)

    memory_static_min = ProxyProperty('memory_static_min')
    name_label = ProxyProperty('name_label')
    uuid = ProxyProperty('uuid')
    VCPUs_max = ProxyProperty('VCPUs_max')
    memory_static_max = ProxyProperty('memory_static_max')
    VCPUs_at_startup = ProxyProperty('VCPUs_at_startup')
    memory_dynamic_max = ProxyProperty('memory_dynamic_max')
    power_state = ProxyProperty('power_state')
    name_description = ProxyProperty('name_description')
    memory_dynamic_min = ProxyProperty('memory_dynamic_min')
    memory_overhead = ProxyProperty('memory_overhead')

