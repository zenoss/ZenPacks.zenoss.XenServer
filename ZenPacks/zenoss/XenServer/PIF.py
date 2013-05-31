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

class PIF(DeviceComponent, ManagedEntity):
    meta_type = portal_type = 'PIF'

    Klasses = [DeviceComponent, ManagedEntity]

    IP = None
    MAC = None
    netmask = None
    gateway = None
    uuid = None

    for Klass in Klasses:
        _properties = _properties + getattr(Klass,'_properties', None)

    _properties = _properties + (
        {'id': 'IP', 'type': 'string', 'mode': 'w'},
        {'id': 'MAC', 'type': 'string', 'mode': 'w'},
        {'id': 'netmask', 'type': 'string', 'mode': 'w'},
        {'id': 'gateway', 'type': 'string', 'mode': 'w'},
        {'id': 'uuid', 'type': 'string', 'mode': 'w'},
        )

    for Klass in Klasses:
        _relations = _relations + getattr(Klass, '_relations', None)

    _relations = _relations + (
        ('device', ToOne(ToManyCont, 'Products.ZenModel.Device.Device', 'pifs',)),
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

class IPIFInfo(IComponentInfo):

    IP = schema.TextLine(title=_t(u'IPS'))
    MAC = schema.TextLine(title=_t(u'MACS'))
    netmask = schema.TextLine(title=_t(u'netmasks'))
    gateway = schema.TextLine(title=_t(u'gateways'))
    uuid = schema.TextLine(title=_t(u'uuids'))

class PIFInfo(ComponentInfo):
    implements(IPIFInfo)

    IP = ProxyProperty('IP')
    MAC = ProxyProperty('MAC')
    netmask = ProxyProperty('netmask')
    gateway = ProxyProperty('gateway')
    uuid = ProxyProperty('uuid')

