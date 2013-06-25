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

class VBD(DeviceComponent, ManagedEntity):
    meta_type = portal_type = 'VBD'

    Klasses = [DeviceComponent, ManagedEntity]

    uuid = None
    bootable = None
    status_code = None
    status_detail = None
    current_attached = None
    type = None
    empty = None

    _properties = ()
    for Klass in Klasses:
        _properties = _properties + getattr(Klass,'_properties', ())

    _properties = _properties + (
        {'id': 'uuid', 'type': 'string', 'mode': 'w'},
        {'id': 'bootable', 'type': 'string', 'mode': 'w'},
        {'id': 'status_code', 'type': 'string', 'mode': 'w'},
        {'id': 'status_detail', 'type': 'string', 'mode': 'w'},
        {'id': 'current_attached', 'type': 'string', 'mode': 'w'},
        {'id': 'type', 'type': 'string', 'mode': 'w'},
        {'id': 'empty', 'type': 'string', 'mode': 'w'},
        )

    _relations = ()
    for Klass in Klasses:
        _relations = _relations + getattr(Klass, '_relations', ())

    _relations = _relations + (
        ('device', ToOne(ToManyCont, 'Products.ZenModel.Device.Device', 'vbds',)),
        ('sr', ToOne(ToManyCont, 'ZenPacks.zenoss.XenServer.SR', 'vbds',)),
        ('vdis', ToManyCont(ToOne, 'ZenPacks.zenoss.XenServer.VDI', 'vbd',)),
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

class IVBDInfo(IComponentInfo):
    vdi_count = schema.Int(title=_t(u'Number of VDIS'))

    uuid = schema.TextLine(title=_t(u'uuids'))
    bootable = schema.TextLine(title=_t(u'bootables'))
    status_code = schema.TextLine(title=_t(u'status_codes'))
    status_detail = schema.TextLine(title=_t(u'status_details'))
    current_attached = schema.TextLine(title=_t(u'current_attacheds'))
    type = schema.TextLine(title=_t(u'types'))
    empty = schema.TextLine(title=_t(u'empties'))

class VBDInfo(ComponentInfo):
    implements(IVBDInfo)

    uuid = ProxyProperty('uuid')
    bootable = ProxyProperty('bootable')
    status_code = ProxyProperty('status_code')
    status_detail = ProxyProperty('status_detail')
    current_attached = ProxyProperty('current_attached')
    type = ProxyProperty('type')
    empty = ProxyProperty('empty')


    @property
    def vdi_count():
        # Using countObjects is fast.
        try:
            return self._object.vdis.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.vdis())

