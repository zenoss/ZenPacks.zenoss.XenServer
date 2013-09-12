##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

'''
XenServer device loaders.
'''

import logging
LOG = logging.getLogger('zen.XenServer')

from zope.interface import implements

from Products.Zuul import getFacade
from Products.ZenModel.interfaces import IDeviceLoader


class XenServerEndpointLoader(object):
    '''
    XenServer endpoint loader.

    Used by including lines such as the following in a zenbatchload
    input file::

        /Devices/XenServer loader='XenServer', loader_arg_keys=['name', 'address', 'username', 'password', 'collector']
        my-xenserver-endpoint name='my-xenserver-endpoint', address='xenserver1.example.com', username='root', password='Xen4TW', collector='localhost'
    '''

    implements(IDeviceLoader)

    def load_device(self, dmd, name=None, address=None, username=None, password=None, collector='localhost'):
        if name is None:
            name = address

        if not all((address, username, password)):
            LOG.error(
                "XenServerEndpointLoader: address, username and password are "
                "required arguments")

        return getFacade('xenserver', dmd).add_xenserver(
            name, address, username, password, collector=collector)
