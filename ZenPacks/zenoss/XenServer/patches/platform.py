##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from Products.ZenUtils.Utils import monkeypatch

from ZenPacks.zenoss.XenServer.PIF import PIF
from ZenPacks.zenoss.XenServer.VIF import VIF


def device_macaddresses(device):
    '''
    Return all MAC addresses associated with device.
    '''
    macaddresses = []
    cat = device.dmd.ZenLinkManager._getCatalog(layer=2)
    if cat is not None:
        brains = cat(deviceId=device.getPrimaryId())
        macaddresses.extend(b.macaddress for b in brains if b.macaddress)

    return macaddresses


@monkeypatch('Products.ZenModel.Device.Device')
def xenserver_host(self):
    '''
    Return the XenServer Host running on this device.
    '''
    pif = PIF.findByMAC(self.dmd, device_macaddresses(self))
    if pif:
        return pif.host()


@monkeypatch('Products.ZenModel.Device.Device')
def xenserver_vm(self):
    '''
    Return the XenServer VM on which this device is a guest.
    '''
    vif = VIF.findByMAC(self.dmd, device_macaddresses(self))
    if vif:
        return vif.vm()


@monkeypatch('Products.ZenModel.HardDisk.HardDisk')
def xenserver_pbd(self):
    '''
    Return the XenServer PBD using this disk.
    '''
    xenserver_host = self.device().xenserver_host()
    if xenserver_host:
        pbd_dc_device = '/dev/{}'.format(self.id)
        for pbd in xenserver_host.pbds():
            if pbd.dc_device and pbd.dc_device == pbd_dc_device:
                return pbd


@monkeypatch('Products.ZenModel.HardDisk.HardDisk')
def xenserver_vbd(self):
    '''
    Return the XenServer VBD underlying this disk.
    '''
    xenserver_vm = self.device().xenserver_vm()
    if xenserver_vm:
        for vbd in xenserver_vm.vbds():
            if vbd.vbd_device and vbd.vbd_device == self.id:
                return vbd


@monkeypatch('Products.ZenModel.IpInterface.IpInterface')
def xenserver_pif(self):
    '''
    Return the XenServer PIF using this interface.
    '''
    return PIF.findByMAC(self.dmd, self.macaddress)


@monkeypatch('Products.ZenModel.IpInterface.IpInterface')
def xenserver_vif(self):
    '''
    Return the XenServer VIF underlying this interface.
    '''
    return VIF.findByMAC(self.dmd, self.macaddress)


@monkeypatch('Products.Zuul.routers.device.DeviceRouter')
def getComponentTree(self, uid=None, id=None, **kwargs):
    '''
    Retrieves all of the components set up to be used in a
    tree.

    Overridden to sort XenServer component types in a reasonable way.

    @type  uid: string
    @param uid: Unique identifier of the root of the tree to retrieve
    @type  id: string
    @param id: not used
    @rtype:   [dictionary]
    @return:  Component properties in tree form
    '''
    # original is injected by monkeypatch decorator.
    result = original(self, uid=uid, id=id, **kwargs)

    if self._getFacade().getInfo(uid=uid).meta_type != 'XenServerEndpoint':
        return result

    order = [
        'XenServerPool',
        'XenServerHost',
        'XenServerHostCPU',
        'XenServerPBD',
        'XenServerPIF',
        'XenServerSR',
        'XenServerVDI',
        'XenServerNetwork',
        'XenServerVMAppliance',
        'XenServerVM',
        'XenServerVBD',
        'XenServerVIF',
        ]

    return sorted(result, key=lambda x: order.index(x['id']))
