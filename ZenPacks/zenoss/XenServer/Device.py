#LICENSE HEADER SAMPLE
from zope.interface import implements
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.device import DeviceInfo
from Products.Zuul.interface.device import IDeviceInfo
from Products.Zuul.utils import ZuulMessageFactory as _t
from Products.ZenModel.Device import Device
from Products.ZenRelations.RelSchema import ToManyCont,ToOne

class Device(Device):
    meta_type = portal_type = 'Device'

    Klasses = [Device]

    for Klass in Klasses:
        _relations = _relations + getattr(Klass, '_relations', None)

    _relations = _relations + (
        ('host_cpus', ToManyCont(ToOne, 'ZenPacks.zenoss.XenServer.host_cpu', 'device',)),
        ('hosts', ToManyCont(ToOne, 'ZenPacks.zenoss.XenServer.host', 'device',)),
        ('networks', ToManyCont(ToOne, 'ZenPacks.zenoss.XenServer.network', 'device',)),
        ('pifs', ToManyCont(ToOne, 'ZenPacks.zenoss.XenServer.PIF', 'device',)),
        ('srs', ToManyCont(ToOne, 'ZenPacks.zenoss.XenServer.SR', 'device',)),
        ('vbds', ToManyCont(ToOne, 'ZenPacks.zenoss.XenServer.VBD', 'device',)),
        ('vdis', ToManyCont(ToOne, 'ZenPacks.zenoss.XenServer.VDI', 'device',)),
        ('vifs', ToManyCont(ToOne, 'ZenPacks.zenoss.XenServer.VIF', 'device',)),
        ('vms', ToManyCont(ToOne, 'ZenPacks.zenoss.XenServer.VM', 'device',)),
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

class IDeviceInfo(IDeviceInfo):
    host_count = schema.Int(title=_t(u'Number of hosts))
    host_cpu_count = schema.Int(title=_t(u'Number of host_cpus))
    network_count = schema.Int(title=_t(u'Number of networks))
    vm_count = schema.Int(title=_t(u'Number of VMS))
    vdi_count = schema.Int(title=_t(u'Number of VDIS))
    vbd_count = schema.Int(title=_t(u'Number of VBDS))
    sr_count = schema.Int(title=_t(u'Number of SRS))
    vif_count = schema.Int(title=_t(u'Number of VIFS))
    pif_count = schema.Int(title=_t(u'Number of PIFS))
class DeviceInfo(DeviceInfo):
    implements(IDeviceInfo)

    @property
    def host_count:
        # Using countObjects is fast.
        try:
            return self._object.hosts.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.hosts())

    @property
    def host_cpu_count:
        # Using countObjects is fast.
        try:
            return self._object.host_cpus.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.host_cpus())

    @property
    def network_count:
        # Using countObjects is fast.
        try:
            return self._object.networks.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.networks())

    @property
    def vm_count:
        # Using countObjects is fast.
        try:
            return self._object.vms.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.vms())

    @property
    def vdi_count:
        # Using countObjects is fast.
        try:
            return self._object.vdis.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.vdis())

    @property
    def vbd_count:
        # Using countObjects is fast.
        try:
            return self._object.vbds.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.vbds())

    @property
    def sr_count:
        # Using countObjects is fast.
        try:
            return self._object.srs.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.srs())

    @property
    def vif_count:
        # Using countObjects is fast.
        try:
            return self._object.vifs.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.vifs())

    @property
    def pif_count:
        # Using countObjects is fast.
        try:
            return self._object.pifs.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.pifs())

