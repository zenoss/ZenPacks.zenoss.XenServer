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

from Products.ZenRelations.RelSchema import ToMany, ToManyCont, ToOne
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.utils import ZuulMessageFactory as _t

from ZenPacks.zenoss.XenServer import CLASS_NAME, MODULE_NAME
from ZenPacks.zenoss.XenServer.utils import (
    PooledComponent, IPooledComponentInfo, PooledComponentInfo,
    RelationshipInfoProperty, RelationshipLengthProperty,
    updateToMany, updateToOne,
    id_from_ref, ids_from_refs, int_or_none, float_or_none,
    )


class Host(PooledComponent):
    '''
    Model class for Host. Also known as Server.
    '''

    meta_type = portal_type = 'XenServerHost'

    xenapi_metrics_ref = None
    api_version_major = None
    api_version_minor = None
    api_version_vendor = None
    address = None
    allowed_operations = None
    capabilities = None
    cpu_count = None
    cpu_speed = None
    edition = None
    enabled = None
    hostname = None
    name_description = None
    name_label = None
    sched_policy = None
    memory_total = None

    _properties = PooledComponent._properties + (
        {'id': 'xenapi_metrics_ref', 'type': 'string', 'mode': 'w'},
        {'id': 'api_version_major', 'type': 'string', 'mode': 'w'},
        {'id': 'api_version_minor', 'type': 'string', 'mode': 'w'},
        {'id': 'api_version_vendor', 'type': 'string', 'mode': 'w'},
        {'id': 'address', 'type': 'string', 'mode': 'w'},
        {'id': 'allowed_operations', 'type': 'lines', 'mode': 'w'},
        {'id': 'capabilities', 'type': 'lines', 'mode': 'w'},
        {'id': 'cpu_count', 'type': 'int', 'mode': 'w'},
        {'id': 'cpu_speed', 'type': 'float', 'mode': 'w'},
        {'id': 'edition', 'type': 'string', 'mode': 'w'},
        {'id': 'enabled', 'type': 'boolean', 'mode': 'w'},
        {'id': 'hostname', 'type': 'string', 'mode': 'w'},
        {'id': 'name_description', 'type': 'string', 'mode': 'w'},
        {'id': 'name_label', 'type': 'string', 'mode': 'w'},
        {'id': 'sched_policy', 'type': 'string', 'mode': 'w'},
        {'id': 'memory_total', 'type': 'int', 'mode': 'w'},
        )

    _relations = PooledComponent._relations + (
        ('endpoint', ToOne(ToManyCont, MODULE_NAME['Endpoint'], 'hosts')),
        ('hostcpus', ToManyCont(ToOne, MODULE_NAME['HostCPU'], 'host')),
        ('pbds', ToManyCont(ToOne, MODULE_NAME['PBD'], 'host')),
        ('pifs', ToManyCont(ToOne, MODULE_NAME['PIF'], 'host')),
        ('vms', ToMany(ToOne, MODULE_NAME['VM'], 'host')),
        ('master_for', ToOne(ToOne, MODULE_NAME['Pool'], 'master')),
        ('suspend_image_sr', ToOne(ToMany, MODULE_NAME['SR'], 'suspend_image_for_hosts')),
        ('crash_dump_sr', ToOne(ToMany, MODULE_NAME['SR'], 'crash_dump_for_hosts')),
        ('local_cache_sr', ToOne(ToMany, MODULE_NAME['SR'], 'local_cache_for_hosts')),
        )

    @classmethod
    def objectmap(cls, ref, properties):
        '''
        Return an ObjectMap given XenAPI host ref and properties.
        '''
        if 'uuid' not in properties:
            return {
                'relname': 'hosts',
                'id': id_from_ref,
                }

        title = properties.get('name_label') or properties.get('hostname')

        cpu_info = properties.get('cpu_info', {})

        cpu_speed = float_or_none(cpu_info.get('speed'))
        if cpu_speed:
            cpu_speed = cpu_speed * 1048576  # Convert from MHz to Hz.

        return {
            'relname': 'hosts',
            'id': id_from_ref(ref),
            'title': title,
            'xenapi_ref': ref,
            'xenapi_uuid': properties.get('uuid'),
            'xenapi_metrics_ref': properties.get('metrics'),
            'api_version_major': properties.get('API_version_major'),
            'api_version_minor': properties.get('API_version_minor'),
            'api_version_vendor': properties.get('API_version_vendor'),
            'address': properties.get('address'),
            'allowed_operations': properties.get('allowed_operations'),
            'capabilities': properties.get('capabilities'),
            'cpu_count': int_or_none(cpu_info.get('cpu_count')),
            'cpu_speed': cpu_speed,
            'edition': properties.get('edition'),
            'enabled': properties.get('enabled'),
            'hostname': properties.get('hostname'),
            'name_description': properties.get('name_description'),
            'name_label': properties.get('name_label'),
            'sched_policy': properties.get('sched_policy'),
            'setVMs': ids_from_refs(properties.get('resident_VMs', [])),
            'setSuspendImageSR': id_from_ref(properties.get('suspend_image_sr')),
            'setCrashDumpSR': id_from_ref(properties.get('crash_dump_sr')),
            'setLocalCacheSR': id_from_ref(properties.get('local_cache_sr')),
            }

    @classmethod
    def objectmap_metrics(cls, ref, properties):
        '''
        Return an ObjectMap given XenAPI host ref and host_metrics
        properties.
        '''
        return {
            'relname': 'hosts',
            'id': id_from_ref(ref),
            'memory_total': int_or_none(properties.get('memory_total')),
            }

    @property
    def is_pool_master(self):
        return self.master_for() is not None

    def getVMs(self):
        '''
        Return a sorted list of each vm id related to this host.

        Used by modeling.
        '''

        return sorted(vm.id for vm in self.vms.objectValuesGen())

    def setVMs(self, vm_ids):
        '''
        Update VM relationship given ids.

        Used by modeling.
        '''
        updateToMany(
            relationship=self.vms,
            root=self.device(),
            type_=CLASS_NAME['VM'],
            ids=vm_ids)

    def getMasterFor(self):
        '''
        Return Pool id or None.

        Used by modeling.
        '''
        master_for = self.master_for()
        if master_for:
            return master_for.id

    def setMasterFor(self, pool_id):
        '''
        Set master_for relationship by Pool id.

        Used by modeling.
        '''
        updateToOne(
            relationship=self.master_for,
            root=self.device(),
            type_=CLASS_NAME['Pool'],
            id_=pool_id)

    def getSuspendImageSR(self):
        '''
        Return SR id or None.

        Used by modeling.
        '''
        suspend_image_sr = self.suspend_image_sr()
        if suspend_image_sr:
            return suspend_image_sr.id

    def setSuspendImageSR(self, sr_id):
        '''
        Set suspend_image_sr relationship by SR id.

        Used by modeling.
        '''
        updateToOne(
            relationship=self.suspend_image_sr,
            root=self.device(),
            type_=CLASS_NAME['SR'],
            id_=sr_id)

    def getCrashDumpSR(self):
        '''
        Return SR id or None.

        Used by modeling.
        '''
        crash_dump_sr = self.crash_dump_sr()
        if crash_dump_sr:
            return crash_dump_sr.id

    def setCrashDumpSR(self, sr_id):
        '''
        Set crash_dump_sr relationship by SR id.

        Used by modeling.
        '''
        updateToOne(
            relationship=self.crash_dump_sr,
            root=self.device(),
            type_=CLASS_NAME['SR'],
            id_=sr_id)

    def getLocalCacheSR(self):
        '''
        Return SR id or None.

        Used by modeling.
        '''
        local_cache_sr = self.local_cache_sr()
        if local_cache_sr:
            return local_cache_sr.id

    def setLocalCacheSR(self, sr_id):
        '''
        Set local_cache_sr relationship by SR id.

        Used by modeling.
        '''
        updateToOne(
            relationship=self.local_cache_sr,
            root=self.device(),
            type_=CLASS_NAME['SR'],
            id_=sr_id)

    def xenrrd_prefix(self):
        '''
        Return prefix under which XenServer stores RRD data about this
        component.
        '''
        if self.xenapi_uuid:
            return ('host', self.xenapi_uuid, '')


class IHostInfo(IPooledComponentInfo):
    '''
    API Info interface for Host.
    '''

    api_version_major = schema.TextLine(title=_t(u'API Version Major'))
    api_version_minor = schema.TextLine(title=_t(u'API Version Minor'))
    api_version_vendor = schema.TextLine(title=_t(u'API Version Vendor'))
    address = schema.TextLine(title=_t(u'Address'))
    allowed_operations = schema.TextLine(title=_t(u'Allowed Operations'))
    capabilities = schema.TextLine(title=_t(u'Capabilities'))
    cpu_count = schema.Int(title=_t(u'CPU Count'))
    cpu_speed = schema.Float(title=_t(u'CPU Speed'))
    edition = schema.TextLine(title=_t(u'Edition'))
    enabled = schema.TextLine(title=_t(u'Enabled'))
    hostname = schema.TextLine(title=_t(u'Hostname'))
    is_pool_master = schema.Bool(title=_t(u'Is Pool Master'))
    name_description = schema.TextLine(title=_t(u'Description'))
    name_label = schema.TextLine(title=_t(u'Label'))
    sched_policy = schema.TextLine(title=_t(u'Scheduling Policy'))
    memory_total = schema.Int(title=_t(u'Total Memory'))

    master_for = schema.Entity(title=_t(u'Master for Pool'))
    suspend_image_sr = schema.Entity(title=_t(u'Suspend Image Storage Repository'))
    crash_dump_sr = schema.Entity(title=_t(u'Crash Dump Storage Repository'))
    local_cache_sr = schema.Entity(title=_t(u'Local Cache Storage Repository'))

    hostcpu_count = schema.Int(title=_t(u'Number of Host CPUs'))
    pbd_count = schema.Int(title=_t(u'Number of Block Devices'))
    pif_count = schema.Int(title=_t(u'Number of Network Interfaces'))
    vm_count = schema.Int(title=_t(u'Number of VMs'))


class HostInfo(PooledComponentInfo):
    '''
    API Info adapter factory for Host.
    '''

    implements(IHostInfo)
    adapts(Host)

    xenapi_metrics_ref = ProxyProperty('xenapi_metrics_ref')
    api_version_major = ProxyProperty('api_version_major')
    api_version_minor = ProxyProperty('api_version_minor')
    api_version_vendor = ProxyProperty('api_version_vendor')
    address = ProxyProperty('address')
    allowed_operations = ProxyProperty('allowed_operations')
    capabilities = ProxyProperty('capabilities')
    cpu_count = ProxyProperty('cpu_count')
    cpu_speed = ProxyProperty('cpu_speed')
    edition = ProxyProperty('edition')
    enabled = ProxyProperty('enabled')
    hostname = ProxyProperty('hostname')
    is_pool_master = ProxyProperty('is_pool_master')
    name_description = ProxyProperty('name_description')
    name_label = ProxyProperty('name_label')
    sched_policy = ProxyProperty('sched_policy')
    memory_total = ProxyProperty('memory_total')

    master_for = RelationshipInfoProperty('master_for')
    suspend_image_sr = RelationshipInfoProperty('suspend_image_sr')
    crash_dump_sr = RelationshipInfoProperty('crash_dump_sr')
    local_cache_sr = RelationshipInfoProperty('local_cache_sr')

    hostcpu_count = RelationshipLengthProperty('hostcpus')
    pbd_count = RelationshipLengthProperty('pbds')
    pif_count = RelationshipLengthProperty('pifs')
    vm_count = RelationshipLengthProperty('vms')
