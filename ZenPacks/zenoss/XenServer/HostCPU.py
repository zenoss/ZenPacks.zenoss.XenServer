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
    id_from_ref, int_or_none,
    )


class HostCPU(PooledComponent):
    '''
    Model class for HostCPU.
    '''

    class_label = 'Host CPU'
    class_plural_label = 'Host CPUs'

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
        {'id': 'family', 'label': 'Family', 'type': 'int', 'mode': 'w'},
        {'id': 'features', 'label': 'Features', 'type': 'string', 'mode': 'w'},
        {'id': 'flags', 'label': 'Flags', 'type': 'string', 'mode': 'w'},
        {'id': 'model', 'label': 'Model', 'type': 'string', 'mode': 'w'},
        {'id': 'modelname', 'label': 'Model Name', 'type': 'string', 'mode': 'w'},
        {'id': 'number', 'label': 'Number', 'type': 'int', 'mode': 'w'},
        {'id': 'speed', 'label': 'Speed', 'type': 'int', 'mode': 'w'},
        {'id': 'stepping', 'label': 'Stepping', 'type': 'int', 'mode': 'w'},
        {'id': 'vendor', 'label': 'Vendor', 'type': 'string', 'mode': 'w'},
        )

    _relations = PooledComponent._relations + (
        ('host', ToOne(ToManyCont, MODULE_NAME['Host'], 'hostcpus')),
        )

    @classmethod
    def objectmap(self, ref, properties):
        '''
        Return an ObjectMap given XenAPI host_cpu ref and properties.
        '''
        if 'uuid' not in properties:
            return {
                'compname': 'hosts/{}'.format(id_from_ref(properties['parent'])),
                'relname': 'hostcpus',
                'id': id_from_ref(ref),
                }

        title = properties.get('number') or properties['uuid']

        cpu_speed = int_or_none(properties.get('speed'))
        if cpu_speed:
            cpu_speed = cpu_speed * 1048576  # Convert from MHz to Hz.

        return {
            'compname': 'hosts/{}'.format(id_from_ref(properties.get('host'))),
            'relname': 'hostcpus',
            'id': id_from_ref(ref),
            'title': title,
            'xenapi_ref': ref,
            'xenapi_uuid': properties.get('uuid'),
            'family': int_or_none(properties.get('family')),
            'features': properties.get('features'),
            'flags': properties.get('flags'),
            'model': int_or_none(properties.get('model')),
            'modelname': properties.get('modelname'),
            'number': int_or_none(properties.get('number')),
            'speed': cpu_speed,
            'stepping': int_or_none(properties.get('stepping')),
            'vendor': properties.get('vendor'),
            }

    def xenrrd_prefix(self):
        '''
        Return prefix under which XenServer stores RRD data about this
        component.
        '''
        host_uuid = self.host().xenapi_uuid
        if host_uuid and self.number is not None:
            return ('host', host_uuid, ''.join(('cpu', str(self.number))))


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
    stepping = schema.Int(title=_t(u'Stepping'))
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
