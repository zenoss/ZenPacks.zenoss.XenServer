##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import time

import transaction
from ZODB.transact import transact

from Products.ZenModel.ZDeviceLoader import JobDeviceLoader
from Products.Jobber.jobs import SubprocessJob

# How long to wait after making model changes for zenhub to become
# aware of the changes.
ZENHUB_DELAY = 40


class XenServerCreationJob(SubprocessJob):
    '''
    Job for adding XenServer endpoints.

    Used when a XenServer is added through the web interface or API.
    '''

    @classmethod
    def getJobType(cls):
        return "Add XenServer Endpoint"

    @classmethod
    def getJobDescription(cls, *args, **kwargs):
        return "Add {deviceName} under {devicePath}".format(**kwargs)

    def _run(self, deviceName, performanceMonitor='localhost', zProperties=None):
        loader = JobDeviceLoader(self.dmd)

        @transact
        def createDevice():
            device = loader.load_device(
                deviceName=deviceName,
                devicePath='/XenServer',
                discoverProto='none',
                performanceMonitor=performanceMonitor,
                zProperties=zProperties)

            device._temp_device = False
            return device

        try:
            self.log.info("Created XenServer endpoint device %s", deviceName)
            device = createDevice()
        except Exception:
            transaction.abort()
            self.log.exception("Encountered error. Rolling back initial device add.")
            raise
        else:
            self.log.info(
                "Waiting %s seconds for ZenHub to learn about %s",
                ZENHUB_DELAY, deviceName)

            time.sleep(ZENHUB_DELAY)

            self.log.info("Scheduling immediate modeling job for %s", deviceName)
            return device.collectDevice(background=True)
