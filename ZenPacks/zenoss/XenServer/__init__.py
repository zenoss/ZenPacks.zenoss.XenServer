######################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is
# installed.
#
######################################################################

import logging
LOG = logging.getLogger('zen.XenServer')

import os
import Globals

from Products.ZenModel.Device import Device
from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from Products.ZenRelations.zPropertyCategory import setzPropertyCategory
from Products.ZenRelations.RelSchema import ToManyCont, ToOne
from Products.CMFCore.DirectoryView import registerDirectory
from Products.Zuul.interfaces import ICatalogTool
from Products.ZenUtils.Utils import monkeypatch, unused, zenPath

unused(Globals)

skinsDir = os.path.join(os.path.dirname(__file__), 'skins')
if os.path.isdir(skinsDir):
    registerDirectory(skinsDir, globals())

ZENPACK_NAME = 'ZenPacks.zenoss.XenServer'

# Modules containing model classes. Used by zenchkschema to validate
# bidirectional integrity of defined relationships.
productNames = (
    'Endpoint',
    'Host',
    'HostCPU',
    'Network',
    'PBD',
    'PIF',
    'Pool',
    'SR',
    'VBD',
    'VDI',
    'VIF',
    'VM',
    'VMAppliance',
    )

# Define new device relations.
NEW_DEVICE_RELATIONS = (
    )

NEW_COMPONENT_TYPES = (
    )

# Add new relationships to Device if they don't already exist.
for relname, modname in NEW_DEVICE_RELATIONS:
    if relname not in (x[0] for x in Device._relations):
        Device._relations += (
            (relname, ToManyCont(
                ToOne,
                '.'.join((ZENPACK_NAME, modname)),
                '%s_host' % modname)),
            )

# Useful to avoid making literal string references to module and class names
# throughout the rest of the ZenPack.
MODULE_NAME = {}
CLASS_NAME = {}

for product_name in productNames:
    MODULE_NAME[product_name] = '.'.join([ZENPACK_NAME, product_name])
    CLASS_NAME[product_name] = '.'.join([ZENPACK_NAME, product_name, product_name])

_PACK_Z_PROPS = [
    ('zXenServerAddresses', [], 'lines'),
    ('zXenServerUsername', 'root', 'string'),
    ('zXenServerPassword', '', 'password'),
    ('zXenServerCollectionInterval', 300, 'int'),
    ]

setzPropertyCategory('zXenServerAddresses', 'XenServer')
setzPropertyCategory('zXenServerUsername', 'XenServer')
setzPropertyCategory('zXenServerPassword', 'XenServer')
setzPropertyCategory('zXenServerCollectionInterval', 'XenServer')

_plugins = (
    )


class ZenPack(ZenPackBase):
    packZProperties = _PACK_Z_PROPS

    def install(self, app):
        super(ZenPack, self).install(app)

        if NEW_DEVICE_RELATIONS:
            LOG.info('Adding ZenPacks.zenoss.XenServer relationships to existing devices')
            self._buildDeviceRelations()

        if _plugins:
            self.symlink_plugins()

    def remove(self, app, leaveObjects=False):
        if not leaveObjects:
            if _plugins:
                self.remove_plugin_symlinks()

            if NEW_COMPONENT_TYPES:
                LOG.info('Removing ZenPacks.zenoss.XenServer components')

                # Search the catalog for components of this zenpacks type.
                cat = ICatalogTool(app.zport.dmd)

                for brain in cat.search(types=NEW_COMPONENT_TYPES):
                    component = brain.getObject()
                    component.getPrimaryParent()._delObject(component.id)

            # Remove our Device relations additions.
            if NEW_DEVICE_RELATIONS:
                Device._relations = tuple(
                    [x for x in Device._relations
                        if x[0] not in NEW_DEVICE_RELATIONS])

                LOG.info('Removing ZenPacks.zenoss.XenServer relationships from existing devices')
                self._buildDeviceRelations()

        super(ZenPack, self).remove(app, leaveObjects=leaveObjects)

    def symlink_plugins(self):
        libexec = os.path.join(os.environ.get('ZENHOME'), 'libexec')
        if not os.path.isdir(libexec):
            # Stack installs might not have a $ZENHOME/libexec directory.
            os.mkdir(libexec)

        for plugin in _plugins:
            LOG.info('Linking %s plugin into $ZENHOME/libexec/', plugin)
            plugin_path = zenPath('libexec', plugin)
            os.system('ln -sf "%s" "%s"' % (self.path(plugin), plugin_path))
            os.system('chmod 0755 %s' % plugin_path)

    def remove_plugin_symlinks(self):
        for plugin in _plugins:
            LOG.info('Removing %s link from $ZENHOME/libexec/', plugin)
            os.system('rm -f "%s"' % zenPath('libexec', plugin))

    def _buildDeviceRelations(self):
        for d in self.dmd.Devices.getSubDevicesGen():
            d.buildRelations()


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
