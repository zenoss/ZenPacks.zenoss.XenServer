##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

'''
Unit test for all-things-Impact.
'''

import transaction

from zope.component import subscribers

from Products.Five import zcml

from Products.ZenTestCase.BaseTestCase import BaseTestCase
from Products.ZenUtils.guid.interfaces import IGUIDManager
from Products.ZenUtils.Utils import monkeypatch

from ZenPacks.zenoss.XenServer.utils import guid, require_zenpack
from ZenPacks.zenoss.XenServer.tests.utils import (
    add_contained, add_noncontained,
    )


@monkeypatch('Products.Zuul')
def get_dmd():
    '''
    Retrieve the DMD object. Handle unit test connection oddities.

    This has to be monkeypatched on Products.Zuul instead of
    Products.Zuul.utils because it's already imported into Products.Zuul
    by the time this monkeypatch happens.
    '''
    try:
        # original is injected by the monkeypatch decorator.
        return original()

    except AttributeError:
        connections = transaction.get()._synchronizers.data.values()[:]
        for cxn in connections:
            app = cxn.root()['Application']
            if hasattr(app, 'zport'):
                return app.zport.dmd


def impacts_for(thing):
    '''
    Return a two element tuple.

    First element is a list of object ids impacted by thing. Second element is
    a list of object ids impacting thing.
    '''
    from ZenPacks.zenoss.Impact.impactd.interfaces \
        import IRelationshipDataProvider

    impacted_by = []
    impacting = []

    guid_manager = IGUIDManager(thing.getDmd())
    for subscriber in subscribers([thing], IRelationshipDataProvider):
        for edge in subscriber.getEdges():
            if edge.source == guid(thing):
                impacted_by.append(guid_manager.getObject(edge.impacted).id)
            elif edge.impacted == guid(thing):
                impacting.append(guid_manager.getObject(edge.source).id)

    return (impacted_by, impacting)


def triggers_for(thing):
    '''
    Return a dictionary of triggers for thing.

    Returned dictionary keys will be triggerId of a Trigger instance and
    values will be the corresponding Trigger instance.
    '''
    from ZenPacks.zenoss.Impact.impactd.interfaces import INodeTriggers

    triggers = {}

    for sub in subscribers((thing,), INodeTriggers):
        for trigger in sub.get_triggers():
            triggers[trigger.triggerId] = trigger

    return triggers


def create_endpoint(dmd):
    '''
    Return an Endpoint suitable for Impact functional testing.
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


class TestImpact(BaseTestCase):
    def afterSetUp(self):
        super(TestImpact, self).afterSetUp()

        import Products.ZenEvents
        zcml.load_config('meta.zcml', Products.ZenEvents)

        try:
            import ZenPacks.zenoss.DynamicView
            zcml.load_config('configure.zcml', ZenPacks.zenoss.DynamicView)
        except ImportError:
            return

        try:
            import ZenPacks.zenoss.Impact
            zcml.load_config('meta.zcml', ZenPacks.zenoss.Impact)
            zcml.load_config('configure.zcml', ZenPacks.zenoss.Impact)
        except ImportError:
            return

        import ZenPacks.zenoss.XenServer
        zcml.load_config('configure.zcml', ZenPacks.zenoss.XenServer)

    def endpoint(self):
        '''
        Return a XenServer endpoint device populated in a suitable way
        for Impact testing.
        '''
        if not hasattr(self, '_endpoint'):
            self._endpoint = create_endpoint(self.dmd)

        return self._endpoint

    def assertTriggersExist(self, triggers, expected_trigger_ids):
        '''
        Assert that each expected_trigger_id exists in triggers.
        '''
        for trigger_id in expected_trigger_ids:
            self.assertTrue(
                trigger_id in triggers, 'missing trigger: %s' % trigger_id)

    @require_zenpack('ZenPacks.zenoss.Impact')
    def test_Endpoint(self):
        endpoint = self.endpoint()

        impacts, impacted_by = impacts_for(endpoint)

        # Endpoint -> Host
        self.assertTrue(
            'host1' in impacts,
            'missing impact: {} <- {}'.format('host1', endpoint))

    @require_zenpack('ZenPacks.zenoss.Impact')
    def test_Host(self):
        host1 = self.endpoint().getObjByPath('hosts/host1')

        impacts, impacted_by = impacts_for(host1)

        # Endpoint -> Host
        self.assertTrue(
            'endpoint' in impacted_by,
            'missing impact: {} -> {}'.format('endpoint', host1))

        # PBD -> Host
        self.assertTrue(
            'pbd1' in impacted_by,
            'missing impact: {} -> {}'.format('pbd1', host1))

        # SR -> Host
        self.assertTrue(
            'sr1' in impacted_by,
            'missing impact: {} -> {}'.format('sr1', host1))

        self.assertTrue(
            'sr2' in impacted_by,
            'missing impact: {} -> {}'.format('sr2', host1))

        self.assertTrue(
            'sr3' in impacted_by,
            'missing impact: {} -> {}'.format('sr3', host1))

        # PIF -> Host
        self.assertTrue(
            'pif1' in impacted_by,
            'missing impact: {} -> {}'.format('pif1', host1))

        # Host -> Pool
        self.assertTrue(
            'pool1' in impacts,
            'missing impact: {} <- {}'.format('pool1', host1))

        # Host -> VM
        self.assertTrue(
            'vm1' in impacts,
            'missing impact: {} <- {}'.format('vm1', host1))

    @require_zenpack('ZenPacks.zenoss.Impact')
    def test_Network(self):
        network1 = self.endpoint().getObjByPath('networks/network1')

        impacts, impacted_by = impacts_for(network1)

        # PIF -> Network
        self.assertTrue(
            'pif1' in impacted_by,
            'missing impact: {} -> {}'.format('pif1', network1))

        # Network -> VIF
        self.assertTrue(
            'vif1' in impacts,
            'missing impact: {} <- {}'.format('vif1', network1))

    @require_zenpack('ZenPacks.zenoss.Impact')
    def test_PBD(self):
        pbd1 = self.endpoint().getObjByPath('hosts/host1/pbds/pbd1')

        impacts, impacted_by = impacts_for(pbd1)

        # PBD -> SR
        self.assertTrue(
            'sr1' in impacts,
            'missing impact: {} <- {}'.format('sr1', pbd1))

        # PBD -> Host
        self.assertTrue(
            'host1' in impacts,
            'missing impact: {} <- {}'.format('host1', pbd1))

    @require_zenpack('ZenPacks.zenoss.Impact')
    def test_PIF(self):
        pif1 = self.endpoint().getObjByPath('hosts/host1/pifs/pif1')

        impacts, impacted_by = impacts_for(pif1)

        # PIF -> Network
        self.assertTrue(
            'network1' in impacts,
            'missing impact: {} <- {}'.format('network1', pif1))

        # PIF -> Host
        self.assertTrue(
            'host1' in impacts,
            'missing impact: {} <- {}'.format('host1', pif1))

    @require_zenpack('ZenPacks.zenoss.Impact')
    def test_Pool(self):
        pool1 = self.endpoint().getObjByPath('pools/pool1')

        impacts, impacted_by = impacts_for(pool1)

        # Host -> Pool
        self.assertTrue(
            'host1' in impacted_by,
            'missing impact: {} -> {}'.format('host1', pool1))

        # SR -> Pool
        self.assertTrue(
            'sr1' in impacted_by,
            'missing impact: {} -> {}'.format('sr1', pool1))

        self.assertTrue(
            'sr2' in impacted_by,
            'missing impact: {} -> {}'.format('sr2', pool1))

        self.assertTrue(
            'sr3' in impacted_by,
            'missing impact: {} -> {}'.format('sr3', pool1))

        # Pool -> VM
        self.assertTrue(
            'vm1' in impacts,
            'missing impact: {} <- {}'.format('vm1', pool1))

    @require_zenpack('ZenPacks.zenoss.Impact')
    def test_SR(self):
        sr1 = self.endpoint().getObjByPath('srs/sr1')
        sr2 = self.endpoint().getObjByPath('srs/sr2')
        sr3 = self.endpoint().getObjByPath('srs/sr3')

        sr1_impacts, sr1_impacted_by = impacts_for(sr1)
        sr2_impacts, sr2_impacted_by = impacts_for(sr2)
        sr3_impacts, sr3_impacted_by = impacts_for(sr3)

        # PBD -> SR
        self.assertTrue(
            'pbd1' in sr1_impacted_by,
            'missing impact: {} -> {}'.format('pbd1', sr1))

        # SR -> Host
        self.assertTrue(
            'host1' in sr1_impacts,
            'missing impacts: {} <- {}'.format('host1', sr1))

        self.assertTrue(
            'host1' in sr2_impacts,
            'missing impacts: {} <- {}'.format('host1', sr2))

        self.assertTrue(
            'host1' in sr3_impacts,
            'missing impacts: {} <- {}'.format('host1', sr3))

        # SR -> Pool
        self.assertTrue(
            'pool1' in sr1_impacts,
            'missing impacts: {} <- {}'.format('pool1', sr1))

        self.assertTrue(
            'pool1' in sr2_impacts,
            'missing impacts: {} <- {}'.format('pool1', sr2))

        self.assertTrue(
            'pool1' in sr3_impacts,
            'missing impacts: {} <- {}'.format('pool1', sr3))

        # SR -> VDI
        self.assertTrue(
            'vdi1' in sr1_impacts,
            'missing impacts: {} <- {}'.format('vdi1', sr1))

    @require_zenpack('ZenPacks.zenoss.Impact')
    def test_VBD(self):
        vbd1 = self.endpoint().getObjByPath('vms/vm1/vbds/vbd1')

        impacts, impacted_by = impacts_for(vbd1)

        # VDI -> VBD
        self.assertTrue(
            'vdi1' in impacted_by,
            'missing impact: {} -> {}'.format('vdi1', vbd1))

        # VBD -> VM
        self.assertTrue(
            'vm1' in impacts,
            'missing impact: {} <- {}'.format('vm1', vbd1))

    @require_zenpack('ZenPacks.zenoss.Impact')
    def test_VDI(self):
        vdi1 = self.endpoint().getObjByPath('srs/sr1/vdis/vdi1')

        impacts, impacted_by = impacts_for(vdi1)

        # SR -> VDI
        self.assertTrue(
            'sr1' in impacted_by,
            'missing impact: {} -> {}'.format('sr1', vdi1))

        # VDI -> VBD
        self.assertTrue(
            'vbd1' in impacts,
            'missing impact: {} <- {}'.format('vbd1', vdi1))

    @require_zenpack('ZenPacks.zenoss.Impact')
    def test_VIF(self):
        vif1 = self.endpoint().getObjByPath('vms/vm1/vifs/vif1')

        impacts, impacted_by = impacts_for(vif1)

        # Network -> VIF
        self.assertTrue(
            'network1' in impacted_by,
            'missing impact: {} -> {}'.format('network1', vif1))

        # VIF -> VM
        self.assertTrue(
            'vm1' in impacts,
            'missing impact: {} <- {}'.format('vm1', vif1))

    @require_zenpack('ZenPacks.zenoss.Impact')
    def test_VM(self):
        vm1 = self.endpoint().getObjByPath('vms/vm1')

        impacts, impacted_by = impacts_for(vm1)

        # Host -> VM
        self.assertTrue(
            'host1' in impacted_by,
            'missing impact: {} -> {}'.format('host1', vm1))

        # Pool -> VM
        self.assertTrue(
            'pool1' in impacted_by,
            'missing impact: {} -> {}'.format('pool1', vm1))

        # VBD -> VM
        self.assertTrue(
            'vbd1' in impacted_by,
            'missing impact: {} -> {}'.format('vbd1', vm1))

        # VIF -> VM
        self.assertTrue(
            'vif1' in impacted_by,
            'missing impact: {} -> {}'.format('vif1', vm1))

        # VM -> VMAppliance
        self.assertTrue(
            'vapp1' in impacts,
            'missing impact: {} <- {}'.format('vapp1', vm1))

    @require_zenpack('ZenPacks.zenoss.Impact')
    def test_VMAppliance(self):
        vapp1 = self.endpoint().getObjByPath('vmappliances/vapp1')

        impacts, impacted_by = impacts_for(vapp1)

        # VM -> VMAppliance
        self.assertTrue(
            'vm1' in impacted_by,
            'missing impact: {} -> {}'.format('vm1', vapp1))

    ### Platform #############################################################

    @require_zenpack('ZenPacks.zenoss.Impact')
    def test_Platform_Physical(self):
        linux_dc = self.dmd.Devices.createOrganizer('/Server/Linux')
        linux_server = linux_dc.createInstance('test-linux-host1')

        from Products.ZenModel.IpInterface import IpInterface
        linux_iface = add_contained(linux_server.os, 'interfaces', IpInterface('eth0'))
        linux_iface.macaddress = '00:0c:29:fe:ab:bc'
        linux_iface.index_object()

        from Products.ZenModel.HardDisk import HardDisk
        linux_disk = add_contained(linux_server.hw, 'harddisks', HardDisk('sda3'))

        host1 = self.endpoint().getObjByPath('hosts/host1')
        host1.address = '192.168.66.71'

        pif1 = self.endpoint().getObjByPath('hosts/host1/pifs/pif1')
        pif1.pif_device = linux_iface.id
        pif1.macaddress = linux_iface.macaddress
        pif1.index_object()

        pbd1 = self.endpoint().getObjByPath('hosts/host1/pbds/pbd1')
        pbd1.dc_device = '/dev/{}'.format(linux_disk.id)

        host1_impacts, host1_impacted_by = impacts_for(host1)
        pbd1_impacts, pbd1_impacted_by = impacts_for(pbd1)
        pif1_impacts, pif1_impacted_by = impacts_for(pif1)

        server_impacts, server_impacted_by = impacts_for(linux_server)
        iface_impacts, iface_impacted_by = impacts_for(linux_iface)
        disk_impacts, disk_impacted_by = impacts_for(linux_disk)

        # Physical Server -> Host
        self.assertTrue(
            linux_server.id in host1_impacted_by,
            'missing impact: {} -> {}'.format(linux_server, host1))

        self.assertTrue(
            host1.id in server_impacts,
            'missing impact: {} <- {}'.format(host1, linux_server))

        # Physical Server IpInterface -> PIF
        self.assertTrue(
            linux_iface.id in pif1_impacted_by,
            'missing impact: {} -> {}'.format(linux_iface, pif1))

        self.assertTrue(
            pif1.id in iface_impacts,
            'missing impact: {} <- {}'.format(pif1, linux_iface))

        # Physical Server HardDisk -> PBD
        self.assertTrue(
            linux_disk.id in pbd1_impacted_by,
            'missing impact: {} -> {}'.format(linux_disk, pbd1))

        self.assertTrue(
            pbd1.id in disk_impacts,
            'missing impact: {} <- {}'.format(pbd1, linux_disk))

    @require_zenpack('ZenPacks.zenoss.Impact')
    def test_Platform_Virtual(self):
        linux_dc = self.dmd.Devices.createOrganizer('/Server/Linux')
        linux_server = linux_dc.createInstance('test-linux-guest1')

        from Products.ZenModel.IpInterface import IpInterface
        linux_iface = add_contained(linux_server.os, 'interfaces', IpInterface('eth0'))
        linux_iface.macaddress = '00:0c:29:fe:ab:bc'
        linux_iface.index_object()

        from Products.ZenModel.HardDisk import HardDisk
        linux_disk = add_contained(linux_server.hw, 'harddisks', HardDisk('xvda'))

        vm1 = self.endpoint().getObjByPath('vms/vm1')

        vif1 = self.endpoint().getObjByPath('vms/vm1/vifs/vif1')
        vif1.vif_device = linux_iface.id
        vif1.macaddress = linux_iface.macaddress
        vif1.index_object()

        vbd1 = self.endpoint().getObjByPath('vms/vm1/vbds/vbd1')
        vbd1.vbd_device = linux_disk.id

        vm1_impacts, vm1_impacted_by = impacts_for(vm1)
        vbd1_impacts, vbd1_impacted_by = impacts_for(vbd1)
        vif1_impacts, vif1_impacted_by = impacts_for(vif1)

        server_impacts, server_impacted_by = impacts_for(linux_server)
        iface_impacts, iface_impacted_by = impacts_for(linux_iface)
        disk_impacts, disk_impacted_by = impacts_for(linux_disk)

        # VM -> Guest Device
        self.assertTrue(
            vm1.id in server_impacted_by,
            'missing impact: {} -> {}'.format(vm1, linux_server))

        self.assertTrue(
            linux_server.id in vm1_impacts,
            'missing impact: {} <- {}'.format(linux_server, vm1))

        # PIF -> Guest IpInterface
        self.assertTrue(
            vif1.id in iface_impacted_by,
            'missing impact: {} -> {}'.format(vif1, linux_iface))

        self.assertTrue(
            linux_iface.id in vif1_impacts,
            'missing impact: {} <- {}'.format(linux_iface, vif1))

        # PBD -> Guest HardDisk
        self.assertTrue(
            vbd1.id in disk_impacted_by,
            'missing impact: {} -> {}'.format(vbd1, linux_disk))

        self.assertTrue(
            linux_disk.id in vbd1_impacts,
            'missing impact: {} <- {}'.format(linux_disk, vbd1))

    ### CloudStack ###########################################################

    @require_zenpack('ZenPacks.zenoss.Impact')
    @require_zenpack('ZenPacks.zenoss.CloudStack')
    def test_CloudStack(self):
        try:
            from ZenPacks.zenoss.CloudStack.tests.test_impact import create_cloud
        except ImportError:
            # CloudStack earlier than 1.1 which doesn't have hooks for
            # XenServer impact.
            return

        from ZenPacks.zenoss.XenServer.VM import VM
        from ZenPacks.zenoss.XenServer.VIF import VIF

        # Create CloudStack configuration.
        cs_cloud = create_cloud(self.dmd)

        cs_host = cs_cloud.getObjByPath('zones/zone1/pods/pod1/clusters/cluster1/hosts/host1')
        cs_host.ip_address = '10.11.12.13'
        cs_host.index_object()

        cs_routervm = cs_cloud.getObjByPath('zones/zone1/pods/pod1/routervms/routervm1')
        cs_routervm.linklocal_macaddress = '00:0c:29:fe:ab:bc'
        cs_routervm.index_object()

        cs_systemvm = cs_cloud.getObjByPath('zones/zone1/pods/pod1/systemvms/systemvm1')
        cs_systemvm.linklocal_macaddress = '00:0c:29:fe:ab:bd'
        cs_systemvm.index_object()

        cs_vm = cs_cloud.getObjByPath('zones/zone1/vms/vm1')
        cs_vm.mac_address = '00:0c:29:fe:ab:be'
        cs_vm.index_object()

        # Create XenServer configuration.
        xen_endpoint = self.endpoint()

        xen_host = xen_endpoint.getObjByPath('hosts/host1')
        xen_pif = xen_host.getObjByPath('pifs/pif1')
        xen_pif.ipv4_addresses = [cs_host.ip_address]
        xen_pif.index_object()

        xen_routervm = add_contained(xen_endpoint, 'vms', VM('xen_routervm1'))
        xen_routervm_vif = add_contained(xen_routervm, 'vifs', VIF('xen_routervm1_vif1'))
        xen_routervm_vif.macaddress = cs_routervm.linklocal_macaddress
        xen_routervm_vif.index_object()

        xen_systemvm = add_contained(xen_endpoint, 'vms', VM('xen_systemvm1'))
        xen_systemvm_vif = add_contained(xen_systemvm, 'vifs', VIF('xen_systemvm1_vif1'))
        xen_systemvm_vif.macaddress = cs_systemvm.linklocal_macaddress
        xen_systemvm_vif.index_object()

        xen_vm = xen_endpoint.getObjByPath('vms/vm1')
        xen_vm_vif = xen_vm.getObjByPath('vifs/vif1')
        xen_vm_vif.macaddress = cs_vm.mac_address
        xen_vm_vif.index_object()

        xen_host_impacts, xen_host_impacted_by = impacts_for(xen_host)
        xen_vm_impacts, vm_impacted_by = impacts_for(xen_vm)
        xen_routervm_impacts, xen_routervm_impacted_by = impacts_for(xen_routervm)
        xen_systemvm_impacts, xen_systemvm_impacted_by = impacts_for(xen_systemvm)

        # Host -> CloudStack Host
        self.assertTrue(
            cs_host.id in xen_host_impacts,
            'missing impact: {0} <- {1}'.format(cs_host, xen_host))

        # VM -> CloudStack RouterVM
        self.assertTrue(
            cs_routervm.id in xen_routervm_impacts,
            'missing impact: {0} <- {1}'.format(cs_routervm, xen_routervm))

        # VM -> CloudStack SystemVM
        self.assertTrue(
            cs_systemvm.id in xen_systemvm_impacts,
            'missing impact: {0} <- {1}'.format(cs_systemvm, xen_systemvm))

        # VM -> CloudStack VirtualMachine
        self.assertTrue(
            cs_vm.id in xen_vm_impacts,
            'missing impact: {0} <- {1}'.format(cs_vm, xen_vm))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestImpact))
    return suite
