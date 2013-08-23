##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

'''
API interfaces and default implementations.
'''

from zope.interface import implements

from Products.ZenUtils.Ext import DirectRouter, DirectResponse

from Products import Zuul
from Products.Zuul.facades import ZuulFacade
from Products.Zuul.interfaces import IFacade

from ZenPacks.zenoss.XenServer.jobs import XenServerCreationJob


class IXenServerFacade(IFacade):
    '''
    Python API interface.
    '''

    def add_xenserver(self, title, address, username, password, collector='localhost'):
        '''
        Schedule the addition of a XenServer.
        '''


class XenServerFacade(ZuulFacade):
    '''
    Python API implementation.
    '''

    implements(IXenServerFacade)

    def add_xenserver(self, name, address, username, password, collector='localhost'):
        zProps = {
            'zXenServerAddresses': [address],
            'zXenServerUsername': username,
            'zXenServerPassword': password,
            }

        kwargs = {
            'deviceName': name,
            'devicePath': '/XenServer',
            'title': name,
            'discoverProto': 'none',
            'performanceMonitor': collector,
            'zProperties': zProps,
            }

        jobManager = self._dmd.JobManager

        try:
            return jobManager.addJob(XenServerCreationJob, kwargs=kwargs)
        except TypeError:
            # Zenoss 4.1.1 compatibility.
            return jobManager.addJob(XenServerCreationJob, **kwargs)


class XenServerRouter(DirectRouter):
    '''
    ExtJS DirectRouter API implementation.
    '''

    def _getFacade(self):
        return Zuul.getFacade('xenserver', self.context)

    def add_xenserver(self, name, address, username, password, collector='localhost'):
        success = self._getFacade().add_xenserver(
            name, address, username, password, collector=collector)

        if success:
            return DirectResponse.succeed()
        else:
            return DirectResponse.fail("Failed to add XenServer")
