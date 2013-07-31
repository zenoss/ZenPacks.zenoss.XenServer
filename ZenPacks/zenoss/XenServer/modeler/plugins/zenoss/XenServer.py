##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

'''
Model XenServer pools using XenAPI (a.k.a. XAPI).
'''

import logging
LOG = logging.getLogger('zen.XenServer')

import collections

from twisted.internet.defer import DeferredList, inlineCallbacks, returnValue

from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import MultiArgs, ObjectMap, RelationshipMap
from Products.ZenUtils.Utils import prepId

from ZenPacks.zenoss.XenServer import MODULE_NAME
from ZenPacks.zenoss.XenServer.utils import add_local_lib_path

# Allows txxenapi to be imported.
add_local_lib_path()

import txxenapi


XAPI_CLASSES = [
    'SR',
    'VDI',
    'host_metrics',
    'host',
    'host_cpu',
    'PBD',
    'PIF',
    'network',
    'VM_metrics',
    'VM',
    'VBD',
    'VIF',
    'VM_appliance',
    'pool',
    ]


def id_from_ref(ref):
    '''
    Return a component id given a XenAPI OpaqueRef.
    '''
    if not ref or ref == 'OpaqueRef:NULL':
        return None

    return prepId(ref.split(':', 1)[1])


def ids_from_refs(refs):
    '''
    Return list of component ids given a list of XenAPI OpaqueRefs.

    Null references won't be included in the returned list. So it's
    possible that the returned list will be shorter than the passed
    list.
    '''
    ids = []

    for ref in refs:
        id_ = id_from_ref(ref)
        if id_:
            ids.append(id_)

    return ids


def int_or_none(value):
    '''
    Return value converted to int or None if conversion fails.
    '''
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def float_or_none(value):
    '''
    Return value converted to float or None if conversion fails.
    '''
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def to_boolean(value, true_value='true'):
    '''
    Return value converted to boolean.
    '''
    if value == true_value:
        return True
    else:
        return False


class ModelerPluginCacheMixin(object):
    '''
    Mix-in class to allow modeler plugin instances to safely share an
    instance level class per modeling run.

    This is used for when methods need to share data. It is required
    because this modeler plugin instance is persistent across modeling
    cycles and can be used to model multiple devices.
    '''

    def cache_prepare(self, device):
        '''
        Prepare class cache for modeling device.
        '''
        self.device = device
        if not hasattr(self, '_cache'):
            self._cache = {}

        self._cache[self.device.id] = collections.defaultdict(dict)

    def cache_set(self, namespace, key, value):
        '''
        Set the cache value for key in namespace. Return value.
        '''
        if not self.device or not self._cache:
            raise Exception('cache not initialized')

        self._cache[self.device.id][namespace][key] = value

        return value

    def cache_get(self, namespace, key, default=None):
        '''
        Get the cached value for key in namespace.
        '''
        if not self.device or not self._cache:
            raise Exception('cache not initialized')

        return self._cache[self.device.id][namespace].get(key, default)

    def cache_clear(self):
        '''
        Clear class cache for current device.
        '''
        if self.device and self._cache and self.device.id in self._cache:
            del(self._cache[self.device.id])

        self.device = None


class XenServer(PythonPlugin, ModelerPluginCacheMixin):
    deviceProperties = PythonPlugin.deviceProperties + (
        'xenserver_addresses',
        'zXenServerUsername',
        'zXenServerPassword',
        )

    @inlineCallbacks
    def collect(self, device, unused):
        '''
        Asynchronously collect data from device. Return a deferred.
        '''
        LOG.info("Collecting data for device %s", device.id)

        if not device.xenserver_addresses:
            LOG.warn("zXenServerAddresses not set. Modeling aborted")
            returnValue(None)

        if not device.zXenServerUsername:
            LOG.warn("zXenServerUsername not set. Modeling aborted")
            returnValue(None)

        if not device.zXenServerPassword:
            LOG.warn("zXenServerPassword not set. Modeling aborted")
            returnValue(None)

        client = txxenapi.Client(
            device.xenserver_addresses,
            device.zXenServerUsername,
            device.zXenServerPassword)

        # Simultaneously call client.xenapi.xxx.get_all_records() for
        # each XAPI class.
        try:
            results = yield DeferredList([
                getattr(client.xenapi, x).get_all_records() for x in XAPI_CLASSES])
        except Exception, ex:
            LOG.error(
                "%s %s XenAPI error: %s",
                self.device, self.name(), ex)

        try:
            yield client.close()
        except Exception, ex:
            LOG.warn(
                "%s %s failed to logout: %s",
                self.device, self.name(), ex)

        returnValue(results)

    def process(self, device, results, unused):
        '''
        Process results of collect method.

        results is a list of two element tuples where the first element
        is a boolean indicating whether the call was successful or not,
        and the second element is a dictionary keyed by object OpaqueRef
        with a dictionary of properties as the value.

            [
                (success, {'OpaqueRef:xxx-xxx': {...}}),
                (success, {'OpaqueRef:xxx-xxx': {...}}),
            ]

        The list indexes map to the the indexes of XAPI_CLASSES.
        '''
        if results is None:
            return None

        # Check to see if all requests failed.
        if set((x[0], x[1] is not None) for x in results) == [(False, False)]:
            LOG.error("No XenServer API response from %s", device.id)
            return None

        LOG.info("Processing data for device %s", device.id)

        self.cache_prepare(device)

        maps = []

        # Call self.xxx_relmaps(self, respective_results) for each XAPI
        # class.
        for i, xapi_class in enumerate(XAPI_CLASSES):
            if not results[i][0] or results[i][1] is None:
                LOG.error("No %s response from %s", xapi_class, device.id)
                continue

            maps.extend(
                getattr(self, '%s_relmaps' % xapi_class.lower())(
                    results[i][1]))

        # Pick up any other maps that can be built with data cached
        # during the main process loop above. This allows for modeling
        # object not represented 1-for-1 by XAPI_CLASSES.
        maps.extend(self.other_maps())

        self.cache_clear()

        return maps

    def host_metrics_relmaps(self, results):
        '''
        Cache host_metrics data to later be used in host_relmaps.
        '''
        for ref, properties in results.items():
            self.cache_set('host_metrics', ref, properties)

        # This method needs to be a generator of nothing.
        if False:
            yield

    def host_relmaps(self, results):
        '''
        Yield a single hosts RelationshipMap.
        '''
        objmaps = []

        for ref, properties in results.items():
            title = properties.get('name_label') or properties.get('hostname')

            cpu_info = properties.get('cpu_info', {})

            cpu_speed = float_or_none(cpu_info.get('speed'))
            if cpu_speed:
                cpu_speed = cpu_speed * 1048576  # Convert from MHz to Hz.

            metrics = self.cache_get(
                'host_metrics', properties.get('metrics'), {})

            objmaps.append({
                'id': id_from_ref(ref),
                'title': title,
                'xapi_ref': ref,
                'xapi_uuid': properties.get('uuid'),
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
                'metrics_ref': properties.get('metrics'),
                'name_description': properties.get('name_description'),
                'name_label': properties.get('name_label'),
                'sched_policy': properties.get('sched_policy'),
                'memory_total': int_or_none(metrics.get('memory_total')),
                'setVMs': ids_from_refs(properties.get('resident_VMs', [])),
                'setSuspendImageSR': id_from_ref(properties.get('suspend_image_sr')),
                'setCrashDumpSR': id_from_ref(properties.get('crash_dump_sr')),
                'setLocalCacheSR': id_from_ref(properties.get('local_cache_sr')),
                })

            # To be used as a default for containing pool with no name.
            self.cache_set('host_titles', ref, title)

        # Cache API version information for use in other_maps.
        try:
            properties = results.itervalues().next()
        except StopIteration:
            # Who cares if there aren't any hosts?
            pass
        else:
            manufacturer = properties.get('API_version_vendor')
            version_major = properties.get('API_version_major')
            version_minor = properties.get('API_version_minor')

            if manufacturer and version_major and version_minor:
                model = 'XenAPI %s.%s' % (version_major, version_minor)

                self.cache_set('api', 'product', {
                    'manufacturer': manufacturer,
                    'model': model,
                    })

        yield RelationshipMap(
            relname='hosts',
            modname=MODULE_NAME['Host'],
            objmaps=objmaps)

    def host_cpu_relmaps(self, results):
        '''
        Yield a hostcpus RelationshipMap for each host.
        '''
        objmaps = collections.defaultdict(list)

        for ref, properties in results.items():
            title = properties.get('number') or properties['uuid']

            cpu_speed = int_or_none(properties.get('speed'))
            if cpu_speed:
                cpu_speed = cpu_speed * 1048576  # Convert from MHz to Hz.

            objmaps[properties['host']].append({
                'id': id_from_ref(ref),
                'title': title,
                'xapi_ref': ref,
                'xapi_uuid': properties.get('uuid'),
                'family': int_or_none(properties.get('family')),
                'features': properties.get('features'),
                'flags': properties.get('flags'),
                'model': int_or_none(properties.get('model')),
                'modelname': properties.get('modelname'),
                'number': int_or_none(properties.get('number')),
                'speed': cpu_speed,
                'stepping': int_or_none(properties.get('stepping')),
                'vendor': properties.get('vendor'),
                })

        for parent_ref, grouped_objmaps in objmaps.items():
            yield RelationshipMap(
                compname='hosts/%s' % id_from_ref(parent_ref),
                relname='hostcpus',
                modname=MODULE_NAME['HostCPU'],
                objmaps=grouped_objmaps)

    def network_relmaps(self, results):
        '''
        Yield a single networks RelationshipMap.
        '''
        objmaps = []

        for ref, properties in results.items():
            title = properties.get('name_label') or properties['uuid']

            other_config = properties.get('other_config', {})

            objmaps.append({
                'id': id_from_ref(ref),
                'title': title,
                'xapi_ref': ref,
                'xapi_uuid': properties.get('uuid'),
                'mtu': properties.get('MTU'),
                'allowed_operations': properties.get('allowed_operations'),
                'bridge': properties.get('bridge'),
                'default_locking_mode': properties.get('default_locking_mode'),
                'name_description': properties.get('name_description'),
                'name_label': properties.get('name_label'),
                'ipv4_begin': other_config.get('ip_begin'),
                'ipv4_end': other_config.get('ip_end'),
                'is_guest_installer_network': to_boolean(other_config.get('is_guest_installer_network')),
                'is_host_internal_management_network': to_boolean(other_config.get('is_host_internal_management_network')),
                'ipv4_netmask': other_config.get('ipv4_netmask'),
                'setPIFs': ids_from_refs(properties.get('PIFs', [])),
                'setVIFs': ids_from_refs(properties.get('VIFs', [])),
                })

        yield RelationshipMap(
            relname='networks',
            modname=MODULE_NAME['Network'],
            objmaps=objmaps)

    def pbd_relmaps(self, results):
        '''
        Yield a pbds RelationshipMap for each host.
        '''
        objmaps = collections.defaultdict(list)

        for ref, properties in results.items():
            device_config = properties.get('device_config', {})

            title = device_config.get('location') or \
                device_config.get('device') or \
                properties['uuid']

            objmaps[properties['host']].append({
                'id': id_from_ref(ref),
                'title': title,
                'xapi_ref': ref,
                'xapi_uuid': properties.get('uuid'),
                'currently_attached': properties.get('currently_attached'),
                'dc_device': device_config.get('device'),
                'dc_legacy_mode': to_boolean(device_config.get('legacy_mode')),
                'dc_location': device_config.get('location'),
                'setSR': id_from_ref(properties.get('SR')),
                })

        for parent_ref, grouped_objmaps in objmaps.items():
            yield RelationshipMap(
                compname='hosts/%s' % id_from_ref(parent_ref),
                relname='pbds',
                modname=MODULE_NAME['PBD'],
                objmaps=grouped_objmaps)

    def pif_relmaps(self, results):
        '''
        Yield a pifs RelationshipMap for each host.
        '''
        objmaps = collections.defaultdict(list)

        for ref, properties in results.items():
            title = properties.get('device') or properties['uuid']

            # IP is a single string whereas IPv6 is a list.
            ipv4_addresses = [x for x in [properties.get('IP')] if x]
            ipv6_addresses = [x for x in properties.get('IPv6', []) if x]

            vlan = properties.get('VLAN')
            if vlan == '-1':
                vlan = None

            objmaps[properties['host']].append({
                'id': id_from_ref(ref),
                'title': title,
                'xapi_ref': ref,
                'xapi_uuid': properties.get('uuid'),
                'dns': properties.get('dns'),
                'ipv4_addresses': ipv4_addresses,
                'ipv6_addresses': ipv6_addresses,
                'macaddress': properties.get('MAC'),
                'mtu': properties.get('MTU'),
                'vlan': vlan,
                'currently_attached': properties.get('currently_attached'),
                'pif_device': properties.get('device'),
                'disallow_unplug': properties.get('disallow_unplug'),
                'ipv4_gateway': properties.get('gateway'),
                'ipv4_configuration_mode': properties.get('ip_configuration_mode'),
                'ipv6_configuration_mode': properties.get('ipv6_configuration_mode'),
                'ipv6_gateway': properties.get('ipv6_gateway'),
                'management': properties.get('management'),
                'metrics_ref': properties.get('metrics'),
                'ipv4_netmask': properties.get('netmask'),
                'physical': properties.get('physical'),
                'primary_address_type': properties.get('primary_address_type'),
                'setNetwork': id_from_ref(properties.get('network')),
                })

        for parent_ref, grouped_objmaps in objmaps.items():
            yield RelationshipMap(
                compname='hosts/%s' % id_from_ref(parent_ref),
                relname='pifs',
                modname=MODULE_NAME['PIF'],
                objmaps=grouped_objmaps)

    def pool_relmaps(self, results):
        '''
        Yield a single pools RelationshipMap.
        '''
        objmaps = []

        for ref, properties in results.items():
            pool_title = properties.get('name_label')

            # By default pools will not have a name_label. XenCenter
            # shows the master host's name_label in this case. We should
            # do the same.
            if not pool_title:
                master_ref = properties.get('master')
                if master_ref:
                    pool_title = self.cache_get('host_titles', master_ref)

            other_config = properties.get('other_config', {})

            objmaps.append({
                'id': id_from_ref(ref),
                'title': pool_title,
                'xapi_ref': ref,
                'xapi_uuid': properties.get('uuid'),
                'ha_allow_overcommit': properties.get('ha_allow_overcommit'),
                'ha_enabled': properties.get('ha_enabled'),
                'ha_host_failures_to_tolerate': int_or_none(properties.get('ha_host_failures_to_tolerate')),
                'name_description': properties.get('name_description'),
                'name_label': properties.get('name_label'),
                'oc_cpuid_feature_mask': other_config.get('cpuid_feature_mask'),
                'oc_memory_ratio_hvm': other_config.get('memory-ratio-hvm'),
                'oc_memory_ratio_pv': other_config.get('memory-ratio-pv'),
                'vswitch_controller': properties.get('vswitch_controller'),
                'setMaster': id_from_ref(properties.get('master')),
                'setDefaultSR': id_from_ref(properties.get('default_SR')),
                'setSuspendImageSR': id_from_ref(properties.get('suspend_image_SR')),
                'setCrashDumpSR': id_from_ref(properties.get('crash_dump_SR')),
                })

        yield RelationshipMap(
            relname='pools',
            modname=MODULE_NAME['Pool'],
            objmaps=objmaps)

    def sr_relmaps(self, results):
        '''
        Yield a single srs RelationshipMap.
        '''
        objmaps = []

        for ref, properties in results.items():
            title = properties.get('name_label') or properties['uuid']

            sm_config = properties.get('sm_config', {})

            objmaps.append({
                'id': id_from_ref(ref),
                'title': title,
                'xapi_ref': ref,
                'xapi_uuid': properties.get('uuid'),
                'allowed_operations': properties.get('allowed_operations'),
                'content_type': properties.get('content_type'),
                'local_cache_enabled': properties.get('local_cache_enabled'),
                'name_description': properties.get('name_description'),
                'name_label': properties.get('name_label'),
                'physical_size': properties.get('physical_size'),
                'shared': properties.get('shared'),
                'sm_type': sm_config.get('type'),
                'sr_type': properties.get('type'),
                'setPBDs': ids_from_refs(properties.get('PBDs', []))
                })

        yield RelationshipMap(
            relname='srs',
            modname=MODULE_NAME['SR'],
            objmaps=objmaps)

    def vbd_relmaps(self, results):
        '''
        Yield a vbds RelationshipMap for each VM.
        '''
        objmaps = collections.defaultdict(list)

        for ref, properties in results.items():
            title = properties.get('device') or \
                properties.get('userdevice') or \
                properties['uuid']

            objmaps[properties['VM']].append({
                'id': id_from_ref(ref),
                'title': title,
                'xapi_ref': ref,
                'xapi_uuid': properties.get('uuid'),
                'allowed_operations': properties.get('allowed_operations'),
                'bootable': properties.get('bootable'),
                'currently_attached': properties.get('currently_attached'),
                'vbd_device': properties.get('device'),
                'empty': properties.get('empty'),
                'metrics_ref': properties.get('metrics'),
                'mode': properties.get('mode'),
                'storage_lock': properties.get('storage_lock'),
                'vbd_type': properties.get('type'),
                'unpluggable': properties.get('unpluggable'),
                'userdevice': properties.get('userdevice'),
                'setVDI': id_from_ref(properties.get('VDI')),
                })

        for parent_ref, grouped_objmaps in objmaps.items():
            yield RelationshipMap(
                compname='vms/%s' % id_from_ref(parent_ref),
                relname='vbds',
                modname=MODULE_NAME['VBD'],
                objmaps=grouped_objmaps)

    def vdi_relmaps(self, results):
        '''
        Yield a vdis RelationshipMap for each storage repository.
        '''
        objmaps = collections.defaultdict(list)

        for ref, properties in results.items():
            title = properties.get('name_label') or \
                properties.get('location') or \
                properties['uuid']

            objmaps[properties['SR']].append({
                'id': id_from_ref(ref),
                'title': title,
                'xapi_ref': ref,
                'xapi_uuid': properties.get('uuid'),
                'allow_caching': properties.get('allow_caching'),
                'allowed_operations': properties.get('allowed_operations'),
                'is_a_snapshot': properties.get('is_a_snapshot'),
                'location': properties.get('location'),
                'managed': properties.get('managed'),
                'missing': properties.get('missing'),
                'name_description': properties.get('name_description'),
                'name_label': properties.get('name_label'),
                'on_boot': properties.get('on_boot'),
                'read_only': properties.get('read_only'),
                'sharable': properties.get('sharable'),
                'storage_lock': properties.get('storage_lock'),
                'vdi_type': properties.get('type'),
                'virtual_size': properties.get('virtual_size'),
                'setVBDs': ids_from_refs(properties.get('VBDs', [])),
                })

        for ref, ref_objmaps in objmaps.items():
            yield RelationshipMap(
                compname='srs/%s' % id_from_ref(ref),
                relname='vdis',
                modname=MODULE_NAME['VDI'],
                objmaps=ref_objmaps)

    def vif_relmaps(self, results):
        '''
        Yield a vifs RelationshipMap for each VM.
        '''
        objmaps = collections.defaultdict(list)

        for ref, properties in results.items():
            title = properties.get('device') or properties['uuid']

            objmaps[properties['VM']].append({
                'id': id_from_ref(ref),
                'title': title,
                'xapi_ref': ref,
                'xapi_uuid': properties.get('uuid'),
                'macaddress': properties.get('MAC'),
                'mac_autogenerated': properties.get('MAC_autogenerated'),
                'mtu': properties.get('MTU'),
                'allowed_operations': properties.get('allowed_operations'),
                'currently_attached': properties.get('currently_attached'),
                'vif_device': properties.get('device'),
                'ipv4_allowed': properties.get('ipv4_allowed'),
                'ipv6_allowed': properties.get('ipv6_allowed'),
                'locking_mode': properties.get('locking_mode'),
                'metrics_ref': properties.get('metrics_ref'),
                'setNetwork': id_from_ref(properties.get('network')),
                })

        for parent_ref, grouped_objmaps in objmaps.items():
            yield RelationshipMap(
                compname='vms/%s' % id_from_ref(parent_ref),
                relname='vifs',
                modname=MODULE_NAME['VIF'],
                objmaps=grouped_objmaps)

    def vm_metrics_relmaps(self, results):
        '''
        Cache VM_metrics data to later be used in vm_relmaps.
        '''
        for ref, properties in results.items():
            self.cache_set('vm_metrics', ref, properties)

        # This method needs to be a generator of nothing.
        if False:
            yield

    def vm_relmaps(self, results):
        '''
        Yield a single vms RelationshipMap.
        '''
        objmaps = []

        for ref, properties in results.items():
            if properties.get('is_a_snapshot') or \
                    properties.get('is_snapshot_from_vmpp') or \
                    properties.get('is_a_template'):

                continue

            title = properties.get('name_label') or properties['uuid']

            metrics = self.cache_get(
                'vm_metrics', properties.get('metrics'), {})

            objmaps.append({
                'id': id_from_ref(ref),
                'title': title,
                'xapi_ref': ref,
                'xapi_uuid': properties.get('uuid'),
                'hvm_shadow_multiplier': properties.get('HVM_shadow_multiplier'),
                'vcpus_at_startup': int_or_none(properties.get('VCPUs_at_startup')),
                'vcpus_max': int_or_none(properties.get('VCPUs_max')),
                'actions_after_crash': properties.get('actions_after_crash'),
                'actions_after_reboot': properties.get('actions_after_reboot'),
                'actions_after_shutdown': properties.get('actions_after_shutdown'),
                'allowed_operations': properties.get('allowed_operations'),
                'domarch': properties.get('domarch'),
                'domid': int_or_none(properties.get('domid')),
                'guest_metrics_ref': properties.get('guest_metrics'),
                'ha_always_run': properties.get('ha_always_run'),
                'ha_restart_priority': properties.get('ha_restart_priority'),
                'is_a_snapshot': properties.get('is_a_snapshot'),
                'is_a_template': properties.get('is_a_template'),
                'is_control_domain': properties.get('is_control_domain'),
                'is_snapshot_from_vmpp': properties.get('is_snapshot_from_vmpp'),
                'memory_actual': int_or_none(metrics.get('memory_actual')),
                'metrics_ref': properties.get('metrics'),
                'name_description': properties.get('name_description'),
                'name_label': properties.get('name_label'),
                'power_state': properties.get('power_state'),
                'shutdown_delay': int_or_none(properties.get('shutdown_delay')),
                'start_delay': int_or_none(properties.get('start_delay')),
                'user_version': int_or_none(properties.get('user_version')),
                'version': int_or_none(properties.get('version')),
                'setHost': id_from_ref(properties.get('resident_on')),
                'setVMAppliance': id_from_ref(properties.get('appliance')),
                })

        yield RelationshipMap(
            relname='vms',
            modname=MODULE_NAME['VM'],
            objmaps=objmaps)

    def vm_appliance_relmaps(self, results):
        '''
        Yield a single vmappliances RelationshipMap.
        '''
        objmaps = []

        for ref, properties in results.items():
            title = properties.get('name_label') or properties['uuid']

            objmaps.append({
                'id': id_from_ref(ref),
                'title': title,
                'setVMs': ids_from_refs(properties.get('VMs', [])),
                })

        yield RelationshipMap(
            relname='vmappliances',
            modname=MODULE_NAME['VMAppliance'],
            objmaps=objmaps)

    def other_maps(self):
        '''
        Yield DataMaps that don't map directly to one of the
        XAPI_CLASSES through their respective *_relmaps methods.
        '''
        # This information is gathered from the host call. So it should
        # be cached in the host_relmaps method.
        api = self.cache_get('api', 'product')
        if api:
            yield ObjectMap(compname='os', data={
                'setProductKey': MultiArgs(api['model'], api['manufacturer']),
                })
