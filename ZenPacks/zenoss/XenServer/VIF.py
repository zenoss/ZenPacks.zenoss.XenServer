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

class VIF(DeviceComponent, ManagedEntity):
    meta_type = portal_type = 'VIF'

    Klasses = [DeviceComponent, ManagedEntity]

    uuid = None
    status_code = None
    status_detail = None
    MAC = None
    MTU = None
    qos_algorithm_type = None

    for Klass in Klasses:
        _properties = _properties + getattr(Klass,'_properties', None)

    _properties = _properties + (
        {'id': 'uuid', 'type': 'string', 'mode': 'w'},
        {'id': 'status_code', 'type': 'string', 'mode': 'w'},
        {'id': 'status_detail', 'type': 'string', 'mode': 'w'},
        {'id': 'MAC', 'type': 'string', 'mode': 'w'},
        {'id': 'MTU', 'type': 'string', 'mode': 'w'},
        {'id': 'qos_algorithm_type', 'type': 'string', 'mode': 'w'},
        )

    for Klass in Klasses:
        _relations = _relations + getattr(Klass, '_relations', None)

    _relations = _relations + (
        ('device', ToOne(ToManyCont, 'Products.ZenModel.Device.Device', 'vifs',)),
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

class IVIFInfo(IComponentInfo):

    uuid = schema.TextLine(title=_t(u'uuids'))
    status_code = schema.TextLine(title=_t(u'status_codes'))
    status_detail = schema.TextLine(title=_t(u'status_details'))
    MAC = schema.TextLine(title=_t(u'MACS'))
    MTU = schema.TextLine(title=_t(u'MTUS'))
    qos_algorithm_type = schema.TextLine(title=_t(u'qos_algorithm_types'))

class VIFInfo(ComponentInfo):
    implements(IVIFInfo)

    uuid = ProxyProperty('uuid')
    status_code = ProxyProperty('status_code')
    status_detail = ProxyProperty('status_detail')
    MAC = ProxyProperty('MAC')
    MTU = ProxyProperty('MTU')
    qos_algorithm_type = ProxyProperty('qos_algorithm_type')

