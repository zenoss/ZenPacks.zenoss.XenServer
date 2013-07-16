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
from Products.ZenRelations.RelSchema import ToManyCont, ToOne
from ZenPacks.zenoss.XenServer.utils import updateToOne


class VIF(DeviceComponent, ManagedEntity):
    meta_type = portal_type = 'XenServerVIF'

    Klasses = [DeviceComponent, ManagedEntity]

    uuid = None
    status_code = None
    status_detail = None
    MAC = None
    MTU = None
    qos_algorithm_type = None

    _properties = ()
    for Klass in Klasses:
        _properties = _properties + getattr(Klass, '_properties', ())

    _properties = _properties + (
        {'id': 'uuid', 'type': 'string', 'mode': 'w'},
        {'id': 'status_code', 'type': 'string', 'mode': 'w'},
        {'id': 'status_detail', 'type': 'string', 'mode': 'w'},
        {'id': 'MAC', 'type': 'string', 'mode': 'w'},
        {'id': 'MTU', 'type': 'string', 'mode': 'w'},
        {'id': 'qos_algorithm_type', 'type': 'string', 'mode': 'w'},
        )

    _relations = ()
    for Klass in Klasses:
        _relations = _relations + getattr(Klass, '_relations', ())

    _relations = _relations + (
        ('endpoint', ToOne(ToManyCont, 'ZenPacks.zenoss.XenServer.Endpoint', 'vifs',)),
        ('network', ToOne(ToMany, 'ZenPacks.zenoss.XenServer.Network', 'vifs',)),
        ('vm', ToOne(ToManyCont, 'ZenPacks.zenoss.XenServer.VM', 'vifs',)),
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

    def getnetworkId(self):
        '''
        Return network id or None.

        Used by modeling.
        '''
        obj = self.network()
        if obj:
            return obj.id

    def setnetworkId(self, id_):
        '''
        Set network by id.

        Used by modeling.
        '''
        updateToOne(
            relationship=self.network,
            root=self.device(),
            type_='ZenPacks.zenoss.XenServer.Network',
            id_=id_)


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


class VIFPathReporter(DefaultPathReporter):
    def getPaths(self):
        paths = super(VIFPathReporter, self).getPaths()

        obj = self.context.network()
        if obj:
            paths.extend(relPath(obj, 'endpoint'))

        return paths
