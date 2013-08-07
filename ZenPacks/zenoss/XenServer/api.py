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

import time

from zope.event import notify
from zope.interface import implements

from ZODB.transact import transact

from Products.ZenUtils.Ext import DirectRouter, DirectResponse

from Products import Zuul
from Products.ZenUtils.Utils import prepId
from Products.Zuul.catalog.events import IndexingEvent
from Products.Zuul.facades import ZuulFacade
from Products.Zuul.interfaces import IFacade
from Products.Zuul.utils import ZuulMessageFactory as _t


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
        device_id = prepId(name)
        devices = self._dmd.getDmdRoot('Devices')
        device = devices.findDeviceByIdExact(device_id)
        if device:
            return False, _t("A resource named %s already exists." % name)

        @transact
        def create_device():
            device_class = self._dmd.Devices.getOrganizer('/XenServer')

            endpoint = device_class.createInstance(device_id)
            endpoint.title = name
            endpoint.setPerformanceMonitor(collector)
            endpoint.setZenProperty('zXenServerAddresses', [address])
            endpoint.setZenProperty('zXenServerUsername', username)
            endpoint.setZenProperty('zXenServerPassword', password)
            endpoint.index_object()
            notify(IndexingEvent(endpoint))

        # This must be committed before the following model can be
        # scheduled.
        create_device()

        # TODO: Fix this.
        # Sleep to make sure zenhub is ready to service the modeling job
        # when we run collectDevice below.
        time.sleep(10)

        # Schedule a modeling job for the new device.
        endpoint = devices.findDeviceByIdExact(device_id)
        endpoint.collectDevice(setlog=False, background=True)

        return True


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
