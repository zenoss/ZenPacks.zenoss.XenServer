######################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is
# installed.
#
######################################################################

import itertools

from zope.component import adapts
from zope.interface import implements

from Products.ZenRelations.RelSchema import ToMany, ToManyCont, ToOne
from Products.Zuul.catalog.paths import DefaultPathReporter, relPath
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.utils import ZuulMessageFactory as _t

from ZenPacks.zenoss.XenServer import CLASS_NAME, MODULE_NAME
from ZenPacks.zenoss.XenServer.utils import (
    PooledComponent, IPooledComponentInfo, PooledComponentInfo,
    RelationshipInfoProperty, RelationshipLengthProperty,
    updateToOne,
    id_from_ref, int_or_none,
    findIpInterfacesByMAC,
    require_zenpack,
    )


class VM(PooledComponent):
    '''
    Model class for VM.
    '''

    class_label = 'VM'
    class_plural_label = 'VMs'
    order = 20

    meta_type = portal_type = 'XenServerVM'

    xenapi_metrics_ref = None
    xenapi_guest_metrics_ref = None
    hvm_shadow_multiplier = None
    vcpus_at_startup = None
    vcpus_max = None
    actions_after_crash = None
    actions_after_reboot = None
    actions_after_shutdown = None
    allowed_operations = None
    domarch = None
    domid = None
    ha_always_run = None
    ha_restart_priority = None
    is_a_snapshot = None
    is_a_template = None
    is_control_domain = None
    is_snapshot_from_vmpp = None
    memory_actual = None
    name_description = None
    name_label = None
    power_state = None
    shutdown_delay = None
    start_delay = None
    user_version = None
    version = None

    _properties = PooledComponent._properties + (
        {'id': 'xenapi_metrics_ref', 'label': 'XENAPI Metrics Reference', 'type': 'string', 'mode': 'w'},
        {'id': 'xenapi_guest_metrics_ref', 'label': 'XENAPI Guest Metrics Reference', 'type': 'string', 'mode': 'w'},
        {'id': 'hvm_shadow_multiplier', 'label': 'HVM Shadow Multiplier', 'type': 'float', 'mode': 'w'},
        {'id': 'vcpus_at_startup', 'label': 'vCPUs at Startup', 'type': 'int', 'mode': 'w'},
        {'id': 'vcpus_max', 'label': 'Maximum vCPUs', 'type': 'int', 'mode': 'w'},
        {'id': 'actions_after_crash', 'label': 'Actions After Crash', 'type': 'string', 'mode': 'w'},
        {'id': 'actions_after_reboot', 'label': 'Actions After Reboot', 'type': 'string', 'mode': 'w'},
        {'id': 'actions_after_shutdown', 'label': 'Actions After Shutdown', 'type': 'string', 'mode': 'w'},
        {'id': 'allowed_operations', 'label': 'Allowed Operations', 'type': 'lines', 'mode': 'w'},
        {'id': 'domarch', 'label': 'Domain Architecture', 'type': 'string', 'mode': 'w'},
        {'id': 'domid', 'label': 'Domain ID', 'type': 'int', 'mode': 'w'},
        {'id': 'ha_always_run', 'label': 'HA Always Run', 'type': 'boolean', 'mode': 'w'},
        {'id': 'ha_restart_priority', 'label': 'HA Restart Priority', 'type': 'string', 'mode': 'w'},
        {'id': 'is_a_snapshot', 'label': 'Is a Snapshot', 'type': 'boolean', 'mode': 'w'},
        {'id': 'is_a_template', 'label': 'Is a Template', 'type': 'boolean', 'mode': 'w'},
        {'id': 'is_control_domain', 'label': 'Is a Domain', 'type': 'boolean', 'mode': 'w'},
        {'id': 'is_snapshot_from_vmpp', 'label': 'Is a Snapshot from VMPP', 'type': 'boolean', 'mode': 'w'},
        {'id': 'memory_actual', 'label': 'Actual Memory', 'type': 'int', 'mode': 'w'},
        {'id': 'name_description', 'label': 'Description', 'type': 'string', 'mode': 'w'},
        {'id': 'name_label', 'label': 'Label', 'type': 'string', 'mode': 'w'},
        {'id': 'power_state', 'label': 'Power State', 'type': 'string', 'mode': 'w'},
        {'id': 'shutdown_delay', 'label': 'Shutdown Delay', 'type': 'int', 'mode': 'w'},
        {'id': 'start_delay', 'label': 'Start Delay', 'type': 'int', 'mode': 'w'},
        {'id': 'user_version', 'label': 'User Version', 'type': 'int', 'mode': 'w'},
        {'id': 'version', 'label': 'Version', 'type': 'int', 'mode': 'w'},
        )

    _relations = PooledComponent._relations + (
        ('endpoint', ToOne(ToManyCont, MODULE_NAME['Endpoint'], 'vms')),
        ('vbds', ToManyCont(ToOne, MODULE_NAME['VBD'], 'vm')),
        ('vifs', ToManyCont(ToOne, MODULE_NAME['VIF'], 'vm')),
        ('host', ToOne(ToMany, MODULE_NAME['Host'], 'vms')),
        ('vmappliance', ToOne(ToMany, MODULE_NAME['VMAppliance'], 'vms')),
        )

    @property
    def ipv4_addresses(self):
        return tuple(itertools.chain.from_iterable(
            x.ipv4_allowed for x in self.vifs() if x.ipv4_allowed))

    @property
    def mac_addresses(self):
        return tuple(x.macaddress for x in self.vifs() if x.macaddress)

    @classmethod
    def objectmap(cls, ref, properties):
        '''
        Return an ObjectMap given XenAPI VM ref and properties.
        '''
        if not properties:
            return {
                'relname': 'vms',
                'id': id_from_ref(ref),
                }

        if properties.get('is_a_snapshot') or \
                properties.get('is_snapshot_from_vmpp') or \
                properties.get('is_a_template'):

            return

        title = properties.get('name_label') or properties['uuid']

        guest_metrics_ref = properties.get('guest_metrics')
        if guest_metrics_ref == 'OpaqueRef:NULL':
            guest_metrics_ref = None

        return {
            'relname': 'vms',
            'id': id_from_ref(ref),
            'title': title,
            'xenapi_ref': ref,
            'xenapi_metrics_ref': properties.get('metrics'),
            'xenapi_guest_metrics_ref': guest_metrics_ref,
            'xenapi_uuid': properties.get('uuid'),
            'hvm_shadow_multiplier': properties.get('HVM_shadow_multiplier'),
            'vcpus_at_startup': int_or_none(properties.get('VCPUs_at_startup')),
            'vcpus_max': int_or_none(properties.get('VCPUs_max')),
            'actions_after_crash': properties.get('actions_after_crash'),
            'actions_after_reboot': properties.get('actions_after_reboot'),
            'actions_after_shutdown': properties.get('actions_after_shutdown'),
            'allowed_operations': properties.get('allowed_operations'),
            'domarch': properties.get('domarch'),
            'domid': int_or_none(properties.get('domid')),
            'ha_always_run': properties.get('ha_always_run'),
            'ha_restart_priority': properties.get('ha_restart_priority'),
            'is_a_snapshot': properties.get('is_a_snapshot'),
            'is_a_template': properties.get('is_a_template'),
            'is_control_domain': properties.get('is_control_domain'),
            'is_snapshot_from_vmpp': properties.get('is_snapshot_from_vmpp'),
            'name_description': properties.get('name_description'),
            'name_label': properties.get('name_label'),
            'power_state': properties.get('power_state'),
            'shutdown_delay': int_or_none(properties.get('shutdown_delay')),
            'start_delay': int_or_none(properties.get('start_delay')),
            'user_version': int_or_none(properties.get('user_version')),
            'version': int_or_none(properties.get('version')),
            'setHost': id_from_ref(properties.get('resident_on')),
            'setVMAppliance': id_from_ref(properties.get('appliance')),
            }

    @classmethod
    def objectmap_metrics(cls, ref, properties):
        '''
        Return an ObjectMap given XenAPI host ref and host_metrics
        properties.
        '''
        return {
            'relname': 'vms',
            'id': id_from_ref(ref),
            'memory_actual': int_or_none(properties.get('memory_actual')),
            }

    def getHost(self):
        '''
        Return host id or None.

        Used by modeling.
        '''
        host = self.host()
        if host:
            return host.id

    def setHost(self, host_id):
        '''
        Set host by id.

        Used by modeling.
        '''
        updateToOne(
            relationship=self.host,
            root=self.device(),
            type_=CLASS_NAME['Host'],
            id_=host_id)

    def getVMAppliance(self):
        '''
        Return VM appliance id or None.

        Used by modeling.
        '''
        vmappliance = self.vmappliance()
        if vmappliance:
            return vmappliance.id

    def setVMAppliance(self, vmappliance_id):
        '''
        Set VM appliance by id.

        Used by modeling.
        '''
        updateToOne(
            relationship=self.vmappliance,
            root=self.device(),
            type_=CLASS_NAME['VMAppliance'],
            id_=vmappliance_id)

    def getRRDTemplates(self):
        '''
        Return a list of RRDTemplate objects to bind to this VM.
        '''
        template_names = [self.getRRDTemplateName()]

        # Bind the guest template only if guest metrics are available.
        if self.xenapi_guest_metrics_ref:
            template_names.append('{0}Guest'.format(self.getRRDTemplateName()))

        templates = []
        for template_name in template_names:
            template = self.getRRDTemplateByName(template_name)
            if template:
                templates.append(template)

        return templates

    def xenrrd_prefix(self):
        '''
        Return prefix under which XenServer stores RRD data about this
        component.
        '''
        if self.xenapi_uuid:
            return ('vm', self.xenapi_uuid, '')

    def getIconPath(self):
        '''
        Return URL to icon representing objects of this class.
        '''
        return '/++resource++xenserver/img/virtual-server.png'

    def guest_device(self):
        '''
        Return the guest device running in the VM.
        '''
        macaddresses = [x.macaddress for x in self.vifs() if x.macaddress]
        if macaddresses:
            for iface in findIpInterfacesByMAC(self.dmd, macaddresses):
                return iface.device()

    @require_zenpack('ZenPacks.zenoss.CloudStack')
    def cloudstack_routervm(self):
        '''
        Return the associated CloudStack router VM.
        '''
        from ZenPacks.zenoss.CloudStack.RouterVM import RouterVM

        try:
            return RouterVM.findByMAC(self.dmd, self.mac_addresses)
        except AttributeError:
            # The CloudStack RouterVM class didn't gain the findByMAC
            # method until version 1.1 of the ZenPack.
            pass

    @require_zenpack('ZenPacks.zenoss.CloudStack')
    def cloudstack_systemvm(self):
        '''
        Return the associated CloudStack system VM.
        '''
        from ZenPacks.zenoss.CloudStack.SystemVM import SystemVM

        try:
            return SystemVM.findByMAC(self.dmd, self.mac_addresses)
        except AttributeError:
            # The CloudStack SystemVM class didn't gain the findByMAC
            # method until version 1.1 of the ZenPack.
            pass

    @require_zenpack('ZenPacks.zenoss.CloudStack')
    def cloudstack_vm(self):
        '''
        Return the associated CloudStack VirtualMachine.
        '''
        from ZenPacks.zenoss.CloudStack.VirtualMachine import VirtualMachine

        try:
            return VirtualMachine.findByMAC(self.dmd, self.mac_addresses)
        except AttributeError:
            # The CloudStack VirtualMachine class didn't gain the
            # findByMAC method until version 1.1 of the ZenPack.
            pass


class IVMInfo(IPooledComponentInfo):
    '''
    API Info interface for VM.
    '''

    host = schema.Entity(title=_t(u'Host'))
    vmappliance = schema.Entity(title=_t(u'vApp'))
    guest_device = schema.Entity(title=_t(u'Guest Device'))

    hvm_shadow_multiplier = schema.Float(title=_t(u'HVM Shadow Multiplier'))
    vcpus_at_startup = schema.Int(title=_t(u'vCPUs at Startup'))
    vcpus_max = schema.Int(title=_t(u'Maximum vCPUs'))
    actions_after_crash = schema.TextLine(title=_t(u'Actions After Crash'))
    actions_after_reboot = schema.TextLine(title=_t(u'Actions After Reboot'))
    actions_after_shutdown = schema.TextLine(title=_t(u'Actions After Shutdown'))
    allowed_operations = schema.TextLine(title=_t(u'Allowed Operations'))
    domarch = schema.TextLine(title=_t(u'Domain Architecture'))
    domid = schema.Int(title=_t(u'Domain ID'))
    ha_always_run = schema.Bool(title=_t(u'HA Always Run'))
    ha_restart_priority = schema.TextLine(title=_t(u'HA Restart Priority'))
    is_a_snapshot = schema.Bool(title=_t(u'Is a Snapshot'))
    is_a_template = schema.Bool(title=_t(u'Is a Template'))
    is_control_domain = schema.Bool(title=_t(u'Is a Control Domain'))
    is_snapshot_from_vmpp = schema.Bool(title=_t(u'Is a Snapshot from VMPP'))
    memory_actual = schema.Int(title=_t(u'Actual Memory'))
    name_description = schema.TextLine(title=_t(u'Description'))
    name_label = schema.TextLine(title=_t(u'Label'))
    power_state = schema.TextLine(title=_t(u'Power State'))
    shutdown_delay = schema.Int(title=_t(u'Shutdown Delay'))
    start_delay = schema.Int(title=_t(u'Start Delay'))
    user_version = schema.Int(title=_t(u'User Version'))
    version = schema.Int(title=_t(u'Version'))

    vbd_count = schema.Int(title=_t(u'Number of Virtual Block Devices'))
    vif_count = schema.Int(title=_t(u'Number of Virtual Network Interfaces'))


class VMInfo(PooledComponentInfo):
    '''
    API Info adapter factory for VM.
    '''

    implements(IVMInfo)
    adapts(VM)

    host = RelationshipInfoProperty('host')
    vmappliance = RelationshipInfoProperty('vmappliance')
    guest_device = RelationshipInfoProperty('guest_device')

    xenapi_metrics_ref = ProxyProperty('xenapi_metrics_ref')
    xenapi_guest_metrics_ref = ProxyProperty('xenapi_guest_metrics_ref')
    hvm_shadow_multiplier = ProxyProperty('hvm_shadow_multiplier')
    vcpus_at_startup = ProxyProperty('vcpus_at_startup')
    vcpus_max = ProxyProperty('vcpus_max')
    actions_after_crash = ProxyProperty('actions_after_crash')
    actions_after_reboot = ProxyProperty('actions_after_reboot')
    actions_after_shutdown = ProxyProperty('actions_after_shutdown')
    allowed_operations = ProxyProperty('allowed_operations')
    domarch = ProxyProperty('domarch')
    domid = ProxyProperty('domid')
    ha_always_run = ProxyProperty('ha_always_run')
    ha_restart_priority = ProxyProperty('ha_restart_priority')
    is_a_snapshot = ProxyProperty('is_a_snapshot')
    is_a_template = ProxyProperty('is_a_template')
    is_control_domain = ProxyProperty('is_control_domain')
    is_snapshot_from_vmpp = ProxyProperty('is_snapshot_from_vmpp')
    memory_actual = ProxyProperty('memory_actual')
    name_description = ProxyProperty('name_description')
    name_label = ProxyProperty('name_label')
    power_state = ProxyProperty('power_state')
    shutdown_delay = ProxyProperty('shutdown_delay')
    start_delay = ProxyProperty('start_delay')
    user_version = ProxyProperty('user_version')
    version = ProxyProperty('version')

    vbd_count = RelationshipLengthProperty('vbds')
    vif_count = RelationshipLengthProperty('vifs')


class VMPathReporter(DefaultPathReporter):
    '''
    Path reporter for VM.
    '''

    def getPaths(self):
        paths = super(VMPathReporter, self).getPaths()

        host = self.context.host()
        if host:
            paths.extend(relPath(host, 'endpoint'))

        vapp = self.context.vmappliance()
        if vapp:
            paths.extend(relPath(vapp, 'endpoint'))

        return paths
