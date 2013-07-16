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
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.utils import ZuulMessageFactory as _t
from Products.ZenModel.Device import Device
from Products.Zuul.infos.device import DeviceInfo
from Products.Zuul.interfaces import IDeviceInfo
from Products.ZenRelations.RelSchema import ToManyCont, ToOne


class Endpoint(Device):
    meta_type = portal_type = 'Endpoint'

    Klasses = [Device]

    _relations = ()
    for Klass in Klasses:
        _relations = _relations + getattr(Klass, '_relations', ())

    _relations = _relations + (
        ('hostcpus', ToManyCont(ToOne, 'ZenPacks.zenoss.XenServer.HostCPU', 'endpoint',)),
        ('hosts', ToManyCont(ToOne, 'ZenPacks.zenoss.XenServer.Host', 'endpoint',)),
        ('networks', ToManyCont(ToOne, 'ZenPacks.zenoss.XenServer.Network', 'endpoint',)),
        ('pbds', ToManyCont(ToOne, 'ZenPacks.zenoss.XenServer.PBD', 'endpoint',)),
        ('pifs', ToManyCont(ToOne, 'ZenPacks.zenoss.XenServer.PIF', 'endpoint',)),
        ('pools', ToManyCont(ToOne, 'ZenPacks.zenoss.XenServer.Pool', 'endpoint',)),
        ('srs', ToManyCont(ToOne, 'ZenPacks.zenoss.XenServer.SR', 'endpoint',)),
        ('vbds', ToManyCont(ToOne, 'ZenPacks.zenoss.XenServer.VBD', 'endpoint',)),
        ('vdis', ToManyCont(ToOne, 'ZenPacks.zenoss.XenServer.VDI', 'endpoint',)),
        ('vifs', ToManyCont(ToOne, 'ZenPacks.zenoss.XenServer.VIF', 'endpoint',)),
        ('vms', ToManyCont(ToOne, 'ZenPacks.zenoss.XenServer.VM', 'endpoint',)),
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


class IEndpointInfo(IDeviceInfo):
    pool_count = schema.Int(title=_t(u'Number of Pools'))
    host_count = schema.Int(title=_t(u'Number of Hosts'))
    hostcpu_count = schema.Int(title=_t(u'Number of HostCPUs'))
    pbd_count = schema.Int(title=_t(u'Number of PBDS'))
    pif_count = schema.Int(title=_t(u'Number of PIFS'))
    sr_count = schema.Int(title=_t(u'Number of SRS'))
    vdi_count = schema.Int(title=_t(u'Number of VDIS'))
    network_count = schema.Int(title=_t(u'Number of Networks'))
    vm_count = schema.Int(title=_t(u'Number of VMS'))
    vbd_count = schema.Int(title=_t(u'Number of VBDS'))
    vif_count = schema.Int(title=_t(u'Number of VIFS'))


class EndpointInfo(DeviceInfo):
    implements(IEndpointInfo)

    @property
    def pool_count(self):
        # Using countObjects is fast.
        try:
            return self._object.pools.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.pools())

    @property
    def host_count(self):
        # Using countObjects is fast.
        try:
            return self._object.hosts.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.hosts())

    @property
    def hostcpu_count(self):
        # Using countObjects is fast.
        try:
            return self._object.hostcpus.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.hostcpus())

    @property
    def pbd_count(self):
        # Using countObjects is fast.
        try:
            return self._object.pbds.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.pbds())

    @property
    def pif_count(self):
        # Using countObjects is fast.
        try:
            return self._object.pifs.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.pifs())

    @property
    def sr_count(self):
        # Using countObjects is fast.
        try:
            return self._object.srs.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.srs())

    @property
    def vdi_count(self):
        # Using countObjects is fast.
        try:
            return self._object.vdis.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.vdis())

    @property
    def network_count(self):
        # Using countObjects is fast.
        try:
            return self._object.networks.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.networks())

    @property
    def vm_count(self):
        # Using countObjects is fast.
        try:
            return self._object.vms.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.vms())

    @property
    def vbd_count(self):
        # Using countObjects is fast.
        try:
            return self._object.vbds.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.vbds())

    @property
    def vif_count(self):
        # Using countObjects is fast.
        try:
            return self._object.vifs.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.vifs())
