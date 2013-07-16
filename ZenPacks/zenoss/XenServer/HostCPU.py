
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

class HostCPU(DeviceComponent, ManagedEntity):
    meta_type = portal_type = 'XenServerHostCPU'

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

    _properties = ()
    for Klass in Klasses:
        _properties = _properties + getattr(Klass,'_properties', ())

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

    _relations = ()
    for Klass in Klasses:
        _relations = _relations + getattr(Klass, '_relations', ())

    _relations = _relations + (
        ('endpoint', ToOne(ToManyCont, 'ZenPacks.zenoss.XenServer.Endpoint', 'hostcpus',)),
        ('host', ToOne(ToManyCont, 'ZenPacks.zenoss.XenServer.Host', 'hostcpus',)),
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

class IHostCPUInfo(IComponentInfo):

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

class HostCPUInfo(ComponentInfo):
    implements(IHostCPUInfo)

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

