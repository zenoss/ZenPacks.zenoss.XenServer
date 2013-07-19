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
    BaseComponent, IBaseComponentInfo, BaseComponentInfo,
    RelationshipLengthProperty,
    updateToMany,
    )


class Host(BaseComponent):
    '''
    Model class for Host. Also known as Server.
    '''

    meta_type = portal_type = 'XenServerHost'

    name_label = None
    name_description = None
    supported_bootloaders = None
    API_version_minor = None
    edition = None
    external_auth_service_name = None
    patches = None
    ha_statefiles = None
    hostname = None
    capabilities = None
    API_version_vendor = None
    tags = None
    power_on_mode = None
    crashdumps = None
    external_auth_type = None
    sched_policy = None
    other_config = None
    enabled = None
    suspend_image_sr = None
    ha_network_peers = None
    API_version_major = None
    memory_overhead = None

    _properties = BaseComponent._properties + (
        {'id': 'name_label', 'type': 'string', 'mode': 'w'},
        {'id': 'name_description', 'type': 'string', 'mode': 'w'},
        {'id': 'supported_bootloaders', 'type': 'string', 'mode': 'w'},
        {'id': 'API_version_minor', 'type': 'string', 'mode': 'w'},
        {'id': 'edition', 'type': 'string', 'mode': 'w'},
        {'id': 'external_auth_service_name', 'type': 'string', 'mode': 'w'},
        {'id': 'patches', 'type': 'string', 'mode': 'w'},
        {'id': 'ha_statefiles', 'type': 'string', 'mode': 'w'},
        {'id': 'hostname', 'type': 'string', 'mode': 'w'},
        {'id': 'capabilities', 'type': 'string', 'mode': 'w'},
        {'id': 'API_version_vendor', 'type': 'string', 'mode': 'w'},
        {'id': 'tags', 'type': 'string', 'mode': 'w'},
        {'id': 'power_on_mode', 'type': 'string', 'mode': 'w'},
        {'id': 'crashdumps', 'type': 'string', 'mode': 'w'},
        {'id': 'external_auth_type', 'type': 'string', 'mode': 'w'},
        {'id': 'sched_policy', 'type': 'string', 'mode': 'w'},
        {'id': 'other_config', 'type': 'string', 'mode': 'w'},
        {'id': 'enabled', 'type': 'string', 'mode': 'w'},
        {'id': 'suspend_image_sr', 'type': 'string', 'mode': 'w'},
        {'id': 'ha_network_peers', 'type': 'string', 'mode': 'w'},
        {'id': 'API_version_major', 'type': 'string', 'mode': 'w'},
        {'id': 'memory_overhead', 'type': 'string', 'mode': 'w'},
        )

    _relations = BaseComponent._relations + (
        ('endpoint', ToOne(ToManyCont, MODULE_NAME['Endpoint'], 'hosts',)),
        ('hostcpus', ToManyCont(ToOne, MODULE_NAME['HostCPU'], 'host',)),
        ('pbds', ToManyCont(ToOne, MODULE_NAME['PBD'], 'host',)),
        ('pifs', ToManyCont(ToOne, MODULE_NAME['PIF'], 'host',)),
        ('vms', ToMany(ToOne, MODULE_NAME['VM'], 'host',)),
        )

    def getVMIds(self):
        '''
        Return a sorted list of each vm id related to this host.

        Used by modeling.
        '''

        return sorted(vm.id for vm in self.vms.objectValuesGen())

    def setVMIds(self, ids):
        '''
        Update VM relationship given ids.

        Used by modeling.
        '''
        updateToMany(
            relationship=self.vms,
            root=self.device(),
            type_=CLASS_NAME['VM'],
            ids=ids)


class IHostInfo(IBaseComponentInfo):
    '''
    API Info interface for Host.
    '''

    name_label = schema.TextLine(title=_t(u'name_labels'))
    name_description = schema.TextLine(title=_t(u'name_descriptions'))
    supported_bootloaders = schema.TextLine(title=_t(u'supported_bootloader'))
    API_version_minor = schema.TextLine(title=_t(u'API_version_minors'))
    edition = schema.TextLine(title=_t(u'editions'))
    external_auth_service_name = schema.TextLine(title=_t(u'external_auth_service_names'))
    patches = schema.TextLine(title=_t(u'patch'))
    ha_statefiles = schema.TextLine(title=_t(u'ha_statefile'))
    hostname = schema.TextLine(title=_t(u'hostnames'))
    capabilities = schema.TextLine(title=_t(u'capability'))
    API_version_vendor = schema.TextLine(title=_t(u'API_version_vendors'))
    tags = schema.TextLine(title=_t(u'tag'))
    power_on_mode = schema.TextLine(title=_t(u'power_on_modes'))
    crashdumps = schema.TextLine(title=_t(u'crashdump'))
    external_auth_type = schema.TextLine(title=_t(u'external_auth_types'))
    sched_policy = schema.TextLine(title=_t(u'sched_policies'))
    other_config = schema.TextLine(title=_t(u'other_configs'))
    enabled = schema.TextLine(title=_t(u'enableds'))
    suspend_image_sr = schema.TextLine(title=_t(u'suspend_image_srs'))
    ha_network_peers = schema.TextLine(title=_t(u'ha_network_peer'))
    API_version_major = schema.TextLine(title=_t(u'API_version_majors'))
    memory_overhead = schema.TextLine(title=_t(u'memory_overheads'))

    pbd_count = schema.Int(title=_t(u'Number of PBDS'))
    hostcpu_count = schema.Int(title=_t(u'Number of HostCPUs'))
    pif_count = schema.Int(title=_t(u'Number of PIFS'))
    vm_count = schema.Int(title=_t(u'Number of VMS'))


class HostInfo(BaseComponentInfo):
    '''
    API Info adapter factory for Host.
    '''

    implements(IHostInfo)
    adapts(Host)

    name_label = ProxyProperty('name_label')
    name_description = ProxyProperty('name_description')
    supported_bootloaders = ProxyProperty('supported_bootloaders')
    API_version_minor = ProxyProperty('API_version_minor')
    edition = ProxyProperty('edition')
    external_auth_service_name = ProxyProperty('external_auth_service_name')
    patches = ProxyProperty('patches')
    ha_statefiles = ProxyProperty('ha_statefiles')
    hostname = ProxyProperty('hostname')
    capabilities = ProxyProperty('capabilities')
    API_version_vendor = ProxyProperty('API_version_vendor')
    tags = ProxyProperty('tags')
    power_on_mode = ProxyProperty('power_on_mode')
    crashdumps = ProxyProperty('crashdumps')
    external_auth_type = ProxyProperty('external_auth_type')
    sched_policy = ProxyProperty('sched_policy')
    other_config = ProxyProperty('other_config')
    enabled = ProxyProperty('enabled')
    suspend_image_sr = ProxyProperty('suspend_image_sr')
    ha_network_peers = ProxyProperty('ha_network_peers')
    API_version_major = ProxyProperty('API_version_major')
    memory_overhead = ProxyProperty('memory_overhead')

    pbd_count = RelationshipLengthProperty('pbds')
    hostcpu_count = RelationshipLengthProperty('hostcpus')
    pif_count = RelationshipLengthProperty('pifs')
    vm_count = RelationshipLengthProperty('vms')
