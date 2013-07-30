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
    PooledComponent, IPooledComponentInfo, PooledComponentInfo,
    RelationshipInfoProperty,
    )


class HostCPU(PooledComponent):
    '''
    Model class for HostCPU.
    '''

    meta_type = portal_type = 'XenServerHostCPU'

    family = None
    features = None
    flags = None
    model = None
    modelname = None
    number = None
    speed = None
    stepping = None
    vendor = None

    _properties = PooledComponent._properties + (
        {'id': 'family', 'type': 'int', 'mode': 'w'},
        {'id': 'features', 'type': 'string', 'mode': 'w'},
        {'id': 'flags', 'type': 'string', 'mode': 'w'},
        {'id': 'model', 'type': 'string', 'mode': 'w'},
        {'id': 'modelname', 'type': 'string', 'mode': 'w'},
        {'id': 'number', 'type': 'int', 'mode': 'w'},
        {'id': 'speed', 'type': 'int', 'mode': 'w'},
        {'id': 'stepping', 'type': 'string', 'mode': 'w'},
        {'id': 'vendor', 'type': 'string', 'mode': 'w'},
        )

    _relations = PooledComponent._relations + (
        ('host', ToOne(ToManyCont, MODULE_NAME['Host'], 'hostcpus')),
        )


class IHostCPUInfo(IPooledComponentInfo):
    '''
    API Info interface for HostCPU.
    '''

    host = schema.Entity(title=_t(u'Host'))

    family = schema.Int(title=_t(u'Family'))
    features = schema.TextLine(title=_t(u'Features'))
    flags = schema.TextLine(title=_t(u'Flags'))
    model = schema.TextLine(title=_t(u'Model'))
    modelname = schema.TextLine(title=_t(u'Model Name'))
    number = schema.Int(title=_t(u'Number'))
    speed = schema.Int(title=_t(u'Speed'))
    stepping = schema.TextLine(title=_t(u'Stepping'))
    vendor = schema.TextLine(title=_t(u'Vender'))


class HostCPUInfo(PooledComponentInfo):
    '''
    API Info adapter factory for HostCPU.
    '''

    implements(IHostCPUInfo)
    adapts(HostCPU)

    host = RelationshipInfoProperty('host')

    family = ProxyProperty('family')
    features = ProxyProperty('features')
    flags = ProxyProperty('flags')
    model = ProxyProperty('model')
    modelname = ProxyProperty('modelname')
    number = ProxyProperty('number')
    speed = ProxyProperty('speed')
    stepping = ProxyProperty('stepping')
    vendor = ProxyProperty('vendor')
