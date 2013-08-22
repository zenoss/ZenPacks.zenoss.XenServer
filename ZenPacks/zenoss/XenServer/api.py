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
from Products.ZenModel.ZDeviceLoader import DeviceCreationJob
from Products.ZenUtils.Utils import binPath
from Products.Zuul.facades import ZuulFacade
from Products.Zuul.interfaces import IFacade


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

        zendiscCmd = [
            binPath('zenxenservermodeler'),
            'run', '--now',
            '-d', name,
            '--monitor', collector,
            ]

        kwargs = {
            'deviceName': name,
            'devicePath': '/XenServer',
            'title': name,
            'discoverProto': 'XenAPI',
            'manageIp': '',
            'performanceMonitor': collector,
            'rackSlot': 0,
            'productionState': 1000,
            'comments': '',
            'hwManufacturer': '',
            'hwProductName': '',
            'osManufacturer': '',
            'osProductName': '',
            'priority': 3,
            'tag': '',
            'serialNumber': '',
            'locationPath': '',
            'systemPaths': [],
            'groupPaths': [],
            'zProperties': zProps,
            'zendiscCmd': zendiscCmd,
            }

        try:
            job_status = self._dmd.JobManager.addJob(
                DeviceCreationJob, kwargs=kwargs)
        except TypeError:
            # 4.1.1 compatibility.
            job_status = self._dmd.JobManager.addJob(
                DeviceCreationJob, **kwargs)

        return job_status


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
