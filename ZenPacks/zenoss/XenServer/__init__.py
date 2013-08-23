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

import Globals

from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from Products.ZenRelations.zPropertyCategory import setzPropertyCategory
from Products.ZenUtils.Utils import unused

unused(Globals)

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

# Useful to avoid making literal string references to module and class names
# throughout the rest of the ZenPack.
MODULE_NAME = {}
CLASS_NAME = {}

for product_name in productNames:
    MODULE_NAME[product_name] = '.'.join([ZENPACK_NAME, product_name])
    CLASS_NAME[product_name] = '.'.join([ZENPACK_NAME, product_name, product_name])

setzPropertyCategory('zXenServerAddresses', 'XenServer')
setzPropertyCategory('zXenServerUsername', 'XenServer')
setzPropertyCategory('zXenServerPassword', 'XenServer')
setzPropertyCategory('zXenServerPerfInterval', 'XenServer')
setzPropertyCategory('zXenServerModelInterval', 'XenServer')
setzPropertyCategory('zXenServerEventsInterval', 'XenServer')


class ZenPack(ZenPackBase):
    packZProperties = [
        ('zXenServerAddresses', [], 'lines'),
        ('zXenServerUsername', 'root', 'string'),
        ('zXenServerPassword', '', 'password'),
        ('zXenServerPerfInterval', 300, 'int'),
        ('zXenServerModelInterval', 60, 'int'),
        ('zXenServerEventsInterval', 60, 'int'),
        ]


# Patch last to avoid import recursion problems.
from ZenPacks.zenoss.XenServer import patches
unused(patches)
