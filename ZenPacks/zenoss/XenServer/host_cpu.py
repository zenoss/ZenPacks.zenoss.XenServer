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

class host_cpu(DeviceComponent, ManagedEntity):
    meta_type = portal_type = 'host_cpu'

    Klasses = [DeviceComponent, ManagedEntity]

    modelname = None
    vendor = None
    features = None
    family = None
    number = None
    utilisation = None
    host = None
    flags = None
    stepping = None
    model = None
    speed = None
    uuid = None

    for Klass in Klasses:
        _properties = _properties + getattr(Klass,'_properties', None)

    _properties = _properties + (
        {'id': 'modelname', 'type': 'string', 'mode': 'w'},
        {'id': 'vendor', 'type': 'string', 'mode': 'w'},
        {'id': 'features', 'type': 'string', 'mode': 'w'},
        {'id': 'family', 'type': 'string', 'mode': 'w'},
        {'id': 'number', 'type': 'string', 'mode': 'w'},
        {'id': 'utilisation', 'type': 'string', 'mode': 'w'},
        {'id': 'host', 'type': 'string', 'mode': 'w'},
        {'id': 'flags', 'type': 'string', 'mode': 'w'},
        {'id': 'stepping', 'type': 'string', 'mode': 'w'},
        {'id': 'model', 'type': 'string', 'mode': 'w'},
        {'id': 'speed', 'type': 'string', 'mode': 'w'},
        {'id': 'uuid', 'type': 'string', 'mode': 'w'},
        )

    for Klass in Klasses:
        _relations = _relations + getattr(Klass, '_relations', None)

    _relations = _relations + (
        ('device', ToOne(ToManyCont, 'Products.ZenModel.Device.Device', 'host_cpus',)),
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

class Ihost_cpuInfo(IComponentInfo):

    modelname = schema.TextLine(title=_t(u'modelnames'))
    vendor = schema.TextLine(title=_t(u'vendors'))
    features = schema.TextLine(title=_t(u'feature'))
    family = schema.TextLine(title=_t(u'families'))
    number = schema.TextLine(title=_t(u'numbers'))
    utilisation = schema.TextLine(title=_t(u'utilisations'))
    host = schema.TextLine(title=_t(u'hosts'))
    flags = schema.TextLine(title=_t(u'flag'))
    stepping = schema.TextLine(title=_t(u'steppings'))
    model = schema.TextLine(title=_t(u'models'))
    speed = schema.TextLine(title=_t(u'speeds'))
    uuid = schema.TextLine(title=_t(u'uuids'))

class host_cpuInfo(ComponentInfo):
    implements(Ihost_cpuInfo)

    modelname = ProxyProperty('modelname')
    vendor = ProxyProperty('vendor')
    features = ProxyProperty('features')
    family = ProxyProperty('family')
    number = ProxyProperty('number')
    utilisation = ProxyProperty('utilisation')
    host = ProxyProperty('host')
    flags = ProxyProperty('flags')
    stepping = ProxyProperty('stepping')
    model = ProxyProperty('model')
    speed = ProxyProperty('speed')
    uuid = ProxyProperty('uuid')

