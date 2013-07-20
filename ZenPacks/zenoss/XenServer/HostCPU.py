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
    RelationshipInfoProperty,
    )


class HostCPU(BaseComponent):
    '''
    Model class for HostCPU.
    '''

    meta_type = portal_type = 'XenServerHostCPU'

    number = None
    speed = None
    stepping = None
    family = None
    vendor = None
    modelname = None
    features = None
    flags = None

    _properties = BaseComponent._properties + (
        {'id': 'number', 'type': 'int', 'mode': 'w'},
        {'id': 'speed', 'type': 'int', 'mode': 'w'},
        {'id': 'stepping', 'type': 'string', 'mode': 'w'},
        {'id': 'family', 'type': 'int', 'mode': 'w'},
        {'id': 'vendor', 'type': 'string', 'mode': 'w'},
        {'id': 'modelname', 'type': 'string', 'mode': 'w'},
        {'id': 'features', 'type': 'string', 'mode': 'w'},
        {'id': 'flags', 'type': 'string', 'mode': 'w'},
        )

    _relations = BaseComponent._relations + (
        ('host', ToOne(ToManyCont, MODULE_NAME['Host'], 'hostcpus')),
        )


class IHostCPUInfo(IBaseComponentInfo):
    '''
    API Info interface for HostCPU.
    '''

    host = schema.Entity(title=_t(u'Host'))
    number = schema.Int(title=_t(u'Number'))
    speed = schema.Int(title=_t(u'Speed'))
    stepping = schema.TextLine(title=_t(u'Stepping'))
    family = schema.Int(title=_t(u'Family'))
    vendor = schema.TextLine(title=_t(u'Vender'))
    modelname = schema.TextLine(title=_t(u'Model'))
    features = schema.TextLine(title=_t(u'Features'))
    flags = schema.TextLine(title=_t(u'Flags'))


class HostCPUInfo(BaseComponentInfo):
    '''
    API Info adapter factory for HostCPU.
    '''

    implements(IHostCPUInfo)
    adapts(HostCPU)

    host = RelationshipInfoProperty('host')
    number = ProxyProperty('number')
    speed = ProxyProperty('speed')
    stepping = ProxyProperty('stepping')
    family = ProxyProperty('family')
    vendor = ProxyProperty('vendor')
    modelname = ProxyProperty('modelname')
    features = ProxyProperty('features')
    flags = ProxyProperty('flags')
