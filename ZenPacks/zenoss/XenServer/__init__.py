##############################################################################
#
# Copyright (C) Zenoss, Inc. 2012, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import logging
LOG = logging.getLogger('zen.XenServer')

from Products.ZenModel.ZenPack import ZenPackBase
# from Products.ZenRelations.zPropertyCategory import setzPropertyCategory


class ZenPack(ZenPackBase):
    """XenServer ZenPack."""

    packZProperties = [
        ('zXenServerPort', '80', 'integer'),
        ('zXenServerUsername', 'root', 'string'),
        ('zXenServerPassword', 'zenoss', 'password'),	# FIXME - hardcodedness
        ('zXenServerUseSSL', False, 'boolean'),
    ]
                                            
                                            
                                            