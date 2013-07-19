######################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is
# installed.
#
######################################################################

from zope.component import adapts
from zope.interface import implements

from Products.ZenRelations.RelSchema import ToManyCont, ToOne
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.utils import ZuulMessageFactory as _t

from ZenPacks.zenoss.XenServer import MODULE_NAME
from ZenPacks.zenoss.XenServer.utils import (
    BaseComponent, IBaseComponentInfo, BaseComponentInfo,
    )


class HostCPU(BaseComponent):
    '''
    Model class for HostCPU.
    '''

    meta_type = portal_type = 'XenServerHostCPU'

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

    _properties = BaseComponent._properties + (
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
        )

    _relations = BaseComponent._relations + (
        ('host', ToOne(ToManyCont, MODULE_NAME['Host'], 'hostcpus')),
        )


class IHostCPUInfo(IBaseComponentInfo):
    '''
    API Info interface for HostCPU.
    '''

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


class HostCPUInfo(BaseComponentInfo):
    '''
    API Info adapter factory for HostCPU.
    '''

    implements(IHostCPUInfo)
    adapts(HostCPU)

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
