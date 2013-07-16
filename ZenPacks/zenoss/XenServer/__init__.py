import logging
log = logging.getLogger('zen.ZenPacks.zenoss.XenServer')

import os
import Globals

from Products.ZenModel.Device import Device
from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from Products.ZenRelations.RelSchema import ToManyCont, ToOne
from Products.ZenRelations.zPropertyCategory import setzPropertyCategory
from Products.CMFCore.DirectoryView import registerDirectory
from Products.Zuul.interfaces import ICatalogTool
from Products.ZenUtils.Utils import unused

unused(Globals)

skinsDir = os.path.join(os.path.dirname(__file__), 'skins')
if os.path.isdir(skinsDir):
    registerDirectory(skinsDir, globals())

ZENPACK_NAME = 'ZenPacks.zenoss.XenServer'

# Modules containing model classes. Used by zenchkschema to validate
# bidirectional integrity of defined relationships.
productNames = (
    'Host',
    'VDI',
    'VBD',
    'PBD',
    'HostCPU',
    'PIF',
    'VM',
    'Endpoint',
    'Network',
    'Pool',
    'VIF',
    'SR',
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
            (relname, ToManyCont(ToOne,
            '.'.join((ZENPACK_NAME, modname)), '%s_host' % modname )),
            )

# Useful to avoid making literal string references to module and class names
# throughout the rest of the ZenPack.
MODULE_NAME={}
CLASS_NAME={}
ZP_NAME='ZenPacks.zenoss.XenServer'
for product_name in productNames:
    MODULE_NAME[product_name]='.'.join([ZP_NAME, product_name])
    CLASS_NAME[product_name]='.'.join([ZP_NAME, product_name, product_name])

_PACK_Z_PROPS=[
               ]


_plugins = (
    )

class ZenPack(ZenPackBase):

    packZProperties = _PACK_Z_PROPS

    def install(self,app):
        super(ZenPack, self).install(app)
        log.info('Adding ZenPacks.zenoss.XenServer relationships to existing devices')

        self._buildDeviceRelations()
        self.symlink_plugins()

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

    def remove(self, app, leaveObjects=False):
        if not leaveObjects:
            self.remove_plugin_symlinks()

            log.info('Removing ZenPacks.zenoss.XenServer components')
            cat = ICatalogTool(app.zport.dmd)

            # Search the catalog for components of this zenpacks type.
            if NEW_COMPONENT_TYPES:
                for brain in cat.search(types=NEW_COMPONENT_TYPES):
                    component = brain.getObject()
                    component.getPrimaryParent()._delObject(component.id)

            # Remove our Device relations additions.
            Device._relations = tuple(
                [x for x in Device._relations \
                    if x[0] not in NEW_DEVICE_RELATIONS])

            log.info('Removing ZenPacks.zenoss.XenServer relationships from existing devices')
            self._buildDeviceRelations()

        super(ZenPack, self).remove(app, leaveObjects=leaveObjects)

    def _buildDeviceRelations(self):
        for d in self.dmd.Devices.getSubDevicesGen():
            d.buildRelations()
