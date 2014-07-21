##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

'''
Model XenServer pools, hosts, PBDs, PIFs, VMs, VBDs, VIFs,
VMAppliances, SRs, VDIs and networks using the XenServer XenAPI.
'''

import logging
LOG = logging.getLogger('zen.XenServer')

from twisted.internet.defer import inlineCallbacks, returnValue

from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin

from ZenPacks.zenoss.XenServer.modeler.incremental import DataMapProducer
from ZenPacks.zenoss.XenServer.utils import add_local_lib_path

# Allows txxenapi to be imported.
add_local_lib_path()

import txxenapi


class XenServer(PythonPlugin):
    deviceProperties = PythonPlugin.deviceProperties + (
        'xenserver_addresses',
        'zXenServerUsername',
        'zXenServerPassword',
        )

    @inlineCallbacks
    def collect(self, device, unused):
        '''
        Asynchronously collect data from device. Return a deferred.
        '''
        LOG.info("Collecting data for device %s", device.id)

        if not device.xenserver_addresses:
            LOG.warn("zXenServerAddresses not set. Modeling aborted")
            returnValue(None)

        if not device.zXenServerUsername:
            LOG.warn("zXenServerUsername not set. Modeling aborted")
            returnValue(None)

        if not device.zXenServerPassword:
            LOG.warn("zXenServerPassword not set. Modeling aborted")
            returnValue(None)

        client = txxenapi.Client(
            device.xenserver_addresses,
            device.zXenServerUsername,
            device.zXenServerPassword)

        producer = DataMapProducer(client)

        try:
            results = yield producer.getmaps()
        except Exception, ex:
            LOG.error(
                "%s %s XenAPI error: %s",
                device.id, self.name(), ex)

        try:
            yield client.close()
        except Exception, ex:
            LOG.warn(
                "%s %s failed to logout: %s",
                device.id, self.name(), ex)

        returnValue(results)

    def process(self, device, results, unused):
        if results is None:
            return None

        LOG.info("Processing data for device %s", device.id)
        return tuple(results)
