###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011, 2012 Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

import logging
LOG = logging.getLogger('zen.XenServer')

from twisted.internet import defer

from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap

from ZenPacks.zenoss.XenServer.utils import addLocalLibPath
from ZenPacks.zenoss.XenServer.lib import XenAPI

from pprint import pprint, pformat
addLocalLibPath()


def fetch_from_xen(sx):
    all_hosts = sx.host.get_all_records()
    all_host_cpus = sx.host_cpu.get_all_records()
    all_VMs = sx.VM.get_all_records()              # A dictionary of virtual machines
    all_VDIs = sx.VDI.get_all_records()              # A dictionary of virtual disk images
    all_VIFs = sx.VIF.get_all_records()              # A dictionary of virtual network interfaces
    all_PIFs = sx.PIF.get_all_records()              # A dictionary of virtual network interfaces
    all_SRs = sx.SR.get_all_records()              # A dictionary of virtual network interfaces
    
    real_VMs = [ x for x in all_VMs if not all_VMs[x]['is_a_template'] and not all_VMs[x]['is_control_domain'] ]

    for vm in real_VMs:
        del real_VMs[vm]['last_booted_record']
    
    return {
        'VMs':      real_VMs, 
        'VDIs':     all_VDIs, 
        'VIFs':     all_VIFs,
        'PIFs':     all_PIFs,
        'hosts':    all_hosts,
        'host_cpus':    all_host_cpus,
        'SRs':      all_SRs,
    }


class XenServer(PythonPlugin):
    deviceProperties = PythonPlugin.deviceProperties + (
        'zXenServerHostname',
        'zXenServerUsername',
        'zXenServerPassword',
        'zXenServerSSL',
        )

    def collect(self, device, unused):
        # if not device.zXenServerHostname:
        #     LOG.error('zXenServerHostname is not set. Not discovering')
        #     return None

        # if not device.zXenServerUsername:
        #     LOG.error('zXenServerUsername is not set. Not discovering')
        #     return None

        # if not device.zXenServerPassword:
        #     LOG.error('zXenServerPassword is not set. Not discovering')
        #     return None

        # if not device.zXenServerSSL:
        #     LOG.error('zXenServerSSL is not set. Not discovering')
        #     return None

        if device.has_attr('zXenServerHostname'):
            session = XenAPI.Session(device.zXenServerHostname)
        else:
            session = XenAPI.Session('http://%s' % device.manageIp)
        session.xenapi.login_with_password(device.zXenServerUsername, device.zXenServerPassword)
        client = session.xenapi

        d = DeferredList((
            fetch_from_xen(client),
            ), consumeErrors=True).addCallback(self.process)

        return d

    def process(self, device, results, unused):
        # See https://dev.zenoss.com/tracint/browser/trunk/enterprise/zenpacks/ZenPacks.zenoss.EMC.base/ZenPacks/zenoss/EMC/base/modeler/emc.py
    
        pprint(results)

        log.info('Modeler %s processing data for server %s',
            self.name(), device.id)

        _om = ObjectMap()

        #Update object to trigger event notification of error
        if results[0] == "ERROR":
            smis_provider_om.setErrorNotification = results[1]
            return smis_provider_om
        else:
            smis_provider_om.setErrorNotification = 'clear'

        maps = []

        # Individual ObjectMaps.
        smis_provider_os_om = ObjectMap(compname='os')

        # ObjectMap lists.
        array_oms = []

        # ObjectMap lists in dictionaries with compname as key.
        map_EC_Battery_oms = collections.defaultdict(list)
        map_EC_DD_oms = collections.defaultdict(list)
        map_EC_LCC_oms = collections.defaultdict(list)
        map_EC_Power_oms = collections.defaultdict(list)
        map_EC_SPC_oms = collections.defaultdict(list)
        map_SPC_PM_oms = collections.defaultdict(list)

        # Lookup maps.
        map_AC_AP = {}
        map_SS_AC = {}
        map_AC_SSSI = {}
        map_SPC_EC = {}
        map_DD_SP = {}
        map_SP_DD = collections.defaultdict(list)
        map_SP_LUN = collections.defaultdict(list)
        map_SPC_IP = {}
        map_ME_StatsInstanceID = {}
        map_DE_DN = {}

        for success, instances in results:
            if not success:
                log.warn("WBEM: %s %s", device.id, result_errmsg(instances))
                continue

            if len(instances) < 1:
                continue

            # There's lots of subclasses going on. We want to treat
            # CIM_DiskDrive, EMC_DiskDrive, Clar_DiskDrive and Symm_DiskDrive
            # the same.
            class_suffix = instances[0].classname.split('_', 1)[-1]

            for instance in instances:

                ### Classes for which there should be exactly one instance.

                # SE_ObjectManager contains high level information about the
                # CIM server and administrator contact information.
                if class_suffix == 'ObjectManager':
                    if 'Name' in instance:
                        smis_provider_om.snmpSysName = \
                            smis_provider_om.title = \
                            smis_provider_om.wbemName = instance['Name']

                    if 'PrimaryOwnerContact' in instance:
                        smis_provider_om.snmpContact = \
                            smis_provider_om.wbemPrimaryOwnerContact = \
                                instance['PrimaryOwnerContact']

                # SE_ManagementServerSoftwareIdentity contains SMI-S provider
                # and SE (Solutions Enabler) version information.
                elif class_suffix == 'ManagementServerSoftwareIdentity':
                    if 'ElementName' in instance:
                        manufacturer, model = \
                            instance['ElementName'].split(' ', 1)

                        if 'EMCSEVersionString' in instance:
                            model = '%s (SE %s)' % (
                                model, instance['EMCSEVersionString'])

                        smis_provider_os_om.setProductKey = \
                            MultiArgs(model, manufacturer)

                # *_QueryStatisticsCollection contains statistics collection
                # information. Most importantly the statistics sample interval.
                # We don't want to query for statistics more frequently than
                # they're updated.
                elif class_suffix == 'QueryStatisticsCollection':
                    try:
                        cim_date = instance['SampleInterval']
                        smis_provider_om.wbemStatsSampleInterval = \
                            cim_date.timedelta.seconds
                        if smis_provider_om.wbemStatsSampleInterval == 0:
                            smis_provider_om.wbemStatsSampleInterval = 300

                    except (AttributeError, KeyError):
                        pass

                ### Classes for which we simply need a list of ObjectMaps.

                elif class_suffix == 'ArrayChassis':
                    array_oms.append(self.get_array_om(instance))

                elif class_suffix == 'EnclosureChassis':
                    enclosure_oms.append(self.get_enclosure_om(instance))

                elif class_suffix == 'SpCard':
                    spcard_oms.append(self.get_spcard_om(instance))

                elif class_suffix == 'DeviceStoragePool':
                    sp_oms.append(self.get_sp_om(instance))

                elif class_suffix == 'UnifiedStoragePool':
                    sp_oms.append(self.get_sp_om(instance))

                elif class_suffix == 'VirtualProvisioningPool':
                    sp_oms.append(self.get_sp_om(instance))

                elif class_suffix == 'VolumeView':
                    lun_om = self.get_lun_om(instance)
                    if lun_om:
                        lun_oms.append(lun_om)

                ### Classes for which we need a keyed dictionary with ObjectMap
                ### lists as values for associating with specific compnames.

                elif class_suffix == 'BatteryModule':
                    for enc_id, om in self.get_EC_Battery_om(instance).items():
                        map_EC_Battery_oms[enc_id].append(om)

                elif class_suffix == 'DiskDrive':
                    for enc_id, om in self.get_EC_DD_om(instance).items():
                        map_EC_DD_oms[enc_id].append(om)

                elif class_suffix == 'LinkControlCard':
                    for enc_id, om in self.get_EC_LCC_om(instance).items():
                        map_EC_LCC_oms[enc_id].append(om)

                elif class_suffix == 'PortModule':
                    for spcard_id, om in self.get_SPC_PM_om(instance).items():
                        map_SPC_PM_oms[spcard_id].append(om)

                elif class_suffix == 'PowerModule':
                    for enc_id, om in self.get_EC_Power_om(instance).items():
                        map_EC_Power_oms[enc_id].append(om)

                ### Classes used to merge data and create relationships.

                elif class_suffix == 'ArrayProduct':
                    map_AC_AP.update(self.get_AC_AP(instance))

                elif class_suffix == 'StorageSystemSoftwareIdentity':
                    map_AC_SSSI.update(self.get_AC_SSSI(instance))

                elif class_suffix == 'Container_EC_SPC':
                    map_SPC_EC.update(self.get_SPC_EC(instance))

                elif class_suffix == 'RemoteServiceAccessPoint':
                    map_SPC_IP.update(self.get_SPC_IP(instance))

                elif class_suffix == 'ConcreteDependency_DD_DVSP':
                    map_DD_SP.update(self.get_DD_SP(instance))

                elif class_suffix == 'ConcreteDependency_DD_USP':
                    map_DD_SP.update(self.get_DD_SP(instance))

                elif class_suffix.startswith('ElementStatisticalData'):
                    map_ME_StatsInstanceID.update(
                        self.get_ME_StatsInstanceID(instance))

                elif class_suffix == 'StorageSystem':
                    map_SS_AC.update(self.get_SS_AC(instance))

                elif class_suffix == 'ProtocolControllerAccessesUnit_BESPC_DE':
                    map_DE_DN.update(self.get_DE_DN(instance))

            ### Anything unexpected?

                else:
                    log.warn("Unexpected class in results: %s",
                        instance.classname)

                    continue

        ### Merging and mapping.
        # Merge data into Array ObjectMaps.

        for om in array_oms:
            om.wbemStatsInstanceID = map_ME_StatsInstanceID.get(om.id)
            for k, v in map_AC_AP.get(om.id, {}).items():
                setattr(om, k, v)

            for k, v in map_AC_SSSI.get(om.id, {}).items():
                setattr(om, k, v)

            for k, v in map_SS_AC.get(om.id, {}).items():
                setattr(om, k, v)
                setattr(om, 'title', v)

            # VMAX doesn't provide a way to associate drives to enclosures. Our
            # model has drives contained within enclosures, so it's mandatory.
            # For this reason we'll fabricate an enclosure for each array to
            # contain all disks in that array.
            if om.wbemClassName.startswith('Symm'):

                # This allows for a different javascript panel to be called for vmax.
                om.meta_type = 'EMCVMAXArray'
                om.portal_type = om.meta_type

                enclosure_oms.append(ObjectMap(data={
                    'id': '%s_AllDisks' % om.id,
                    'title': '%s All Disks' % om.id,
                    'enclosureState': 'OK',
                    'arrayID': 'none',
                    'logicalID': 'Default All Disks',
                    'setProductKey': MultiArgs('VMAX-1', 'EMC Corporation'),
                    'wbemClassName': 'Symm_EnclosureChassis',
                    'wbemTag': '',
                    }))

        # Merge data for enclosures
        for om in enclosure_oms:
            # Merge in Array name
            for k, v in map_SS_AC.get(self.prepId(om.arrayID), {}).items():
                setattr(om, 'arrayID', v)

        # Merge data into SP ObjectMaps. Map to enclosures.
        for om in spcard_oms:

            # Merge data into SP ObjectMaps.
            om.wbemStatsInstanceID = map_ME_StatsInstanceID.get(om.id)
            om.spIP = map_SPC_IP.get(om.id)

            # Merge in Array name
            for k, v in map_SS_AC.get(self.prepId(om.arrayID), {}).items():
                setattr(om, 'arrayID', v)

            enclosure_id = map_SPC_EC.get(om.id)
            if enclosure_id is not None:
                map_EC_SPC_oms[enclosure_id].append(om)

        # Merge data into HardDisk ObjectMaps.
        for enclosure_id, oms in map_EC_DD_oms.items():
            for om in oms:
                om.wbemStatsInstanceID = map_ME_StatsInstanceID.get(om.id)
                om.spID = map_DD_SP.get(om.id)
                om.driveName = map_DE_DN.get(om.spindleName)

                # Merge in Array name
                for k, v in map_SS_AC.get(self.prepId(om.arrayID), {}).items():
                    setattr(om, 'arrayID', v)

                if om.spID:
                    map_SP_DD[om.spID].append(om.id)

        # Merge data into LUN ObjectMaps.
        for om in lun_oms:

            if om.wbemClassName.startswith('Symm'):
                # This allows for a different javascript panel to be called for vmax.
                om.meta_type = 'EMCVMAXDataDevice'
                om.portal_type = om.meta_type

            try:
                _lunId = int(om.svname, 16)
                setattr(om, 'lunId', _lunId)
            except:
                pass

            om.wbemStatsInstanceID = map_ME_StatsInstanceID.get(om.id)

            # Merge in Array name
            for k, v in map_SS_AC.get(self.prepId(om.arrayID), {}).items():
                setattr(om, 'arrayID', v)

            sp_id = self.prepId(om.wbemSPInstanceID)
            map_SP_LUN[sp_id].append(om.id)

        # Merge data into StoragePool ObjectMaps.
        for om in sp_oms:
            om.setHardDiskIds = sorted(map_SP_DD.get(om.id, []))
            om.setLunIds = sorted(map_SP_LUN.get(om.id, []))

            # Merge in Array name
            for k, v in map_SS_AC.get(self.prepId(om.arrayID), {}).items():
                setattr(om, 'arrayID', v)

        maps.extend([smis_provider_om, smis_provider_os_om])

        maps.append(RelationshipMap(
            relname="arrays",
            modname="ZenPacks.zenoss.EMC.base.Array",
            objmaps=array_oms))

        maps.append(RelationshipMap(
            relname="enclosures",
            compname="hw",
            modname="ZenPacks.zenoss.EMC.base.Enclosure",
            objmaps=enclosure_oms))

        # Fill batteries relationship on each enclosure individually.
        for enclosure_id, oms in map_EC_Battery_oms.items():

            # Merge in Array name
            for om in oms:
                for k, v in map_SS_AC.get(self.prepId(om.arrayID), {}).items():
                    setattr(om, 'arrayID', v)

            maps.append(RelationshipMap(
                relname="batteries",
                compname="hw/enclosures/" + enclosure_id,
                modname="ZenPacks.zenoss.EMC.base.Battery",
                objmaps=oms))

        # Fill disks relationship on each enclosure individually.
        for enclosure_id, oms in map_EC_DD_oms.items():
            maps.append(RelationshipMap(
                relname="disks",
                compname="hw/enclosures/" + enclosure_id,
                modname="ZenPacks.zenoss.EMC.base.HardDisk",
                objmaps=oms))

        # Fill lccs relationship on each enclosure individually.
        for enclosure_id, oms in map_EC_LCC_oms.items():

            # Merge in Array name
            for om in oms:
                for k, v in map_SS_AC.get(self.prepId(om.arrayID), {}).items():
                    setattr(om, 'arrayID', v)

            maps.append(RelationshipMap(
                relname="lccs",
                compname="hw/enclosures/" + enclosure_id,
                modname="ZenPacks.zenoss.EMC.base.LCC",
                objmaps=oms))

        # Fill powersupplies relationship on each enclosure individually.
        for enclosure_id, oms in map_EC_Power_oms.items():

            # Merge in Array name
            for om in oms:
                for k, v in map_SS_AC.get(self.prepId(om.arrayID), {}).items():
                    setattr(om, 'arrayID', v)

            maps.append(RelationshipMap(
                relname="powersupplies",
                compname="hw/enclosures/" + enclosure_id,
                modname="ZenPacks.zenoss.EMC.base.PowerSupply",
                objmaps=oms))

        # Fill spcards relationship on each enclosure individually.
        for enclosure_id, oms in map_EC_SPC_oms.items():
            maps.append(RelationshipMap(
                relname="spcards",
                compname="hw/enclosures/" + enclosure_id,
                modname="ZenPacks.zenoss.EMC.base.SP",
                objmaps=oms))

        # Fill spports relationship on each spcard individually.
        for spcard_id, oms in map_SPC_PM_oms.items():

            # Merge data into SPPort ObjectMaps.
            for om in oms:
                om.wbemStatsInstanceID = map_ME_StatsInstanceID.get(om.id)
                # Merge in Array name
                for k, v in map_SS_AC.get(self.prepId(om.arrayID), {}).items():
                    setattr(om, 'arrayID', v)

            enclosure_id = map_SPC_EC.get(spcard_id)
            if not enclosure_id:
                log.warn("Storage processor %s has no enclosure", spcard_id)
                continue

            compname = 'hw/enclosures/%s/spcards/%s' % (
                enclosure_id, spcard_id)

            maps.append(RelationshipMap(
                relname="spports",
                compname=compname,
                modname="ZenPacks.zenoss.EMC.base.SPPort",
                objmaps=oms))

        maps.append(RelationshipMap(
            relname="luns",
            compname="os",
            modname="ZenPacks.zenoss.EMC.base.LUN",
            objmaps=lun_oms))

        maps.append(RelationshipMap(
            relname="storagepools",
            compname="os",
            modname="ZenPacks.zenoss.EMC.base.StoragePool",
            objmaps=sp_oms))

        return maps
