##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################


def add_contained(obj, relname, target):
    '''
    Add and return obj to containing relname on target.
    '''
    rel = getattr(obj, relname)
    rel._setObject(target.id, target)
    return rel._getOb(target.id)


def add_noncontained(obj, relname, target):
    '''
    Add obj to non-containing relname on target.
    '''
    rel = getattr(obj, relname)
    rel.addRelation(target)


def create_endpoint(dmd):
    '''
    Return an Endpoint suitable for functional testing.
    '''
    # DeviceClass
    dc = dmd.Devices.createOrganizer('/XenServer')
    dc.setZenProperty('zPythonClass', 'ZenPacks.zenoss.XenServer.Endpoint')

    # Endpoint
    endpoint = dc.createInstance('endpoint')

    # Host
    from ZenPacks.zenoss.XenServer.Host import Host
    host1 = add_contained(endpoint, 'hosts', Host('host1'))

    from ZenPacks.zenoss.XenServer.PBD import PBD
    pbd1 = add_contained(host1, 'pbds', PBD('pbd1'))

    from ZenPacks.zenoss.XenServer.PIF import PIF
    pif1 = add_contained(host1, 'pifs', PIF('pif1'))

    # Storage
    from ZenPacks.zenoss.XenServer.SR import SR
    sr1 = add_contained(endpoint, 'srs', SR('sr1'))
    add_noncontained(sr1, 'pbds', pbd1)
    add_noncontained(sr1, 'suspend_image_for_hosts', host1)

    sr2 = add_contained(endpoint, 'srs', SR('sr2'))
    add_noncontained(sr2, 'crash_dump_for_hosts', host1)

    sr3 = add_contained(endpoint, 'srs', SR('sr3'))
    add_noncontained(sr3, 'local_cache_for_hosts', host1)

    from ZenPacks.zenoss.XenServer.VDI import VDI
    vdi1 = add_contained(sr1, 'vdis', VDI('vdi1'))

    # Network
    from ZenPacks.zenoss.XenServer.Network import Network
    network1 = add_contained(endpoint, 'networks', Network('network1'))
    add_noncontained(network1, 'pifs', pif1)

    # Pool
    from ZenPacks.zenoss.XenServer.Pool import Pool
    pool1 = add_contained(endpoint, 'pools', Pool('pool1'))
    add_noncontained(pool1, 'master', host1)
    add_noncontained(pool1, 'default_sr', sr1)
    add_noncontained(pool1, 'suspend_image_sr', sr2)
    add_noncontained(pool1, 'crash_dump_sr', sr3)

    # VM
    from ZenPacks.zenoss.XenServer.VM import VM
    vm1 = add_contained(endpoint, 'vms', VM('vm1'))
    add_noncontained(vm1, 'host', host1)

    from ZenPacks.zenoss.XenServer.VBD import VBD
    vbd1 = add_contained(vm1, 'vbds', VBD('vbd1'))
    add_noncontained(vbd1, 'vdi', vdi1)

    from ZenPacks.zenoss.XenServer.VIF import VIF
    vif1 = add_contained(vm1, 'vifs', VIF('vif1'))
    add_noncontained(vif1, 'network', network1)

    # vApp
    from ZenPacks.zenoss.XenServer.VMAppliance import VMAppliance
    vapp1 = add_contained(endpoint, 'vmappliances', VMAppliance('vapp1'))
    add_noncontained(vapp1, 'vms', vm1)

    return endpoint
