##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import logging
ADM_LOG = logging.getLogger("zen.ApplyDataMap")

from Products.DataCollector.plugins.DataMaps import ObjectMap
from Products.ZenEvents import Event
from Products.ZenEvents.ZenEventClasses import Change_Remove, Change_Remove_Blocked
from Products.ZenModel.Lockable import Lockable
from Products.ZenUtils.Utils import monkeypatch

from ZenPacks.zenoss.XenServer.PIF import findPIFByMAC


@monkeypatch('Products.ZenModel.Device.Device')
def xenserver_host(self):
    '''
    Return the XenServer Host running on this device.
    '''
    macaddresses = []
    cat = self.dmd.ZenLinkManager._getCatalog(layer=2)
    if cat is not None:
        brains = cat(deviceId=self.getPrimaryId())
        macaddresses.extend(b.macaddress for b in brains if b.macaddress)

    pif = findPIFByMAC(self.dmd, macaddresses)
    if pif:
        return pif.host()


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


@monkeypatch('Products.ZenModel.IpInterface.IpInterface')
def xenserver_pif(self):
    '''
    Return the XenServer PIF using this interface.
    '''
    return findPIFByMAC(self.dmd, self.macaddress)


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


@monkeypatch('Products.DataCollector.ApplyDataMap.ApplyDataMap')
def _updateRelationship(self, device, relmap):
    '''
    Add/Update/Remove objects to the target relationship.

    Overridden to catch naked ObjectMaps with relname set. This
    indicates an incremental model that should be specially handled.

    Return True if a change was made or false if no change was made.
    '''
    if not isinstance(ObjectMap, relmap):
        # original is injected by monkeypatch decorator.
        return original(self, device, relmap)

    remove = getattr(relmap, 'remove', False) is True

    if hasattr(relmap, 'remove'):
        del(relmap.remove)

    if hasattr(relmap, 'relname'):
        del(relmap.relname)

    rel = getattr(device, relmap.relname, None)
    if not rel:
        return False

    if remove:
        return self._removeRelObject(device, relmap, relmap.relname)

    obj = rel._getOb(relmap.id, None)
    if obj:
        return self._updateObject(obj, relmap)

    return self._createRelObject(device, relmap, relmap.relname)[0]


@monkeypatch('Products.DataCollector.ApplyDataMap.ApplyDataMap')
def _removeRelObject(self, device, objmap, relname):
    '''
    Remove an object in a relationship using its ObjectMap.

    Return True if a change was made or False if no change was made.
    '''
    rel = getattr(device, objmap.relname, None)
    if not rel:
        return False

    obj = rel._getOb(objmap.id, None)
    if not obj:
        return False

    if isinstance(obj, Lockable) and obj.isLockedFromDeletion():
        msg = "Deletion Blocked: {} '{}' on {}".format(
            obj.meta_type, obj.id, obj.device().id)

        ADM_LOG.warn(msg)
        if obj.sendEventWhenBlocked():
            self.logEvent(
                device, obj, Change_Remove_Blocked, msg, Event.Warning)

        return False

    self.logChange(
        device, obj, Change_Remove,
        "removing object {} from rel {} on {}".format(
            obj.id, objmap.relname, device.id))

    rel._delObject(obj.id)

    return True
