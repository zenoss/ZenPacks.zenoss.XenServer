#!/usr/bin/env python
##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import Globals

import logging
log = logging.getLogger('zen.XenServerModeler')

import json
import sys

from pprint import pformat

import transaction

from twisted.internet import defer
from Products.Five import zcml

from Products.DataCollector.ApplyDataMap import ApplyDataMap
from Products.DataCollector.plugins.DataMaps import ObjectMap
from Products.ZenUtils.Utils import unused
from Products.ZenUtils.ZenScriptBase import ZenScriptBase

import ZenPacks.zenoss.XenServer.locallibs  # for txxen

from ZenPacks.zenoss.XenServer.VIConfig import viAllCollectedMOClasses
from ZenPacks.zenoss.XenServer.VIConfig import viCollectPropertiesForMOClass
from ZenPacks.zenoss.XenServer.VIFullState import VIFullState
from ZenPacks.zenoss.XenServer.VIIncrState import VIIncrState
from ZenPacks.zenoss.XenServer.VIUtil import moidString, moidToId
from ZenPacks.zenoss.XenServer.Util import deviceToGraphviz

import txxen


# Make pyflakes happy.
unused(Globals, ZenPacks.zenoss.XenServer.locallibs)


class XenServerModeler(ZenScriptBase):
    def buildOptions(self):
        ZenScriptBase.buildOptions(self)

        self.parser.add_option(
            '--hostname', dest='hostname',
            help="XenServer hostname (required)")

        self.parser.add_option(
            '--username', dest='username',
            help="XenServer username (required)")

        self.parser.add_option(
            '--password', dest='password',
            help="XenServer password (required)")

        self.parser.add_option(
            '--nossl', dest='noSSL', default=False, action='store_true',
            help="Disable SSL for XenServer client connection")

    def verify_options(self):
        if not self.options.hostname:
            sys.exit("You must specify --hostname")

        if not self.options.username:
            sys.exit("You must specify --username")

        if not self.options.password:
            sys.exit("You must specify --password")

    def get_client(self):
        return txxen.XenServerClient(
            self.options.hostname,
            self.options.username,
            self.options.password,
            not self.options.noSSL)

    @defer.inlineCallbacks
    def run(self):
        zcml.load_config('configure.zcml', ZenPacks.zenoss.XenServer)

        client = self.get_client()

        yield client.connect()

        svc_inst_ref = {
            'type': 'ServiceInstance',
            'value': 'ServiceInstance',
        }

        response = yield client.makeRequest(
            'VimPortType', 'currentTime', svc_inst_ref)

        log.info("CurrentTime=%s", response)

        service_content = yield client.makeRequest(
            'VimPortType', 'retrieveServiceContent', svc_inst_ref)

        view_manager = service_content['viewManager']
        root_folder = service_content['rootFolder']
        prop_collector = service_content['propertyCollector']

        # Configure the propertyfilter to watch for the data we are
        # interested in.

        # Get a list of all the managed object types we'll be watching.
        motypes = viAllCollectedMOClasses()

        # Start with a view of the objects we are interested in. This
        # simplifies our propertyfilterspecs
        container_view = yield client.makeRequest(
            'VimPortType', 'createContainerView',
            view_manager, root_folder, motypes, True)

        prop_filter_spec = {
            'propSet': [],
            'objectSet': [
                {
                    'obj': container_view,
                    'skip': True,
                    'selectSet': [
                        {
                            '@class': 'TraversalSpec',  # Type hint (for polymorphism)
                            'name': 'ContainerViewtraversalview',
                            'type': 'ContainerView',
                            'path': 'view',
                            'skip': False,
                        },
                    ]
                },
                {
                    'obj': root_folder,
                    'skip': False,
                },
            ]
        }

        for motype in motypes:
            properties = viCollectPropertiesForMOClass(motype)

            prop_filter_spec['propSet'].append({
                'type': motype,
                'all': False,
                'pathSet': properties,
            })

        #### RetrievePropertiesEx version
        # all_objects = []
        # Note: the server can enforce a lower number.  On testing, it seems like it likes 100.
        # retrieve_options = {
        #     'maxObjects': 1000
        # }

        # result = yield client.makeRequest('VimPortType', 'retrievePropertiesEx',
        #     prop_collector, [prop_filter_spec], retrieve_options)

        # while True:
        #     print "Retrieved %d objects." % len(result['objects'])
        #     all_objects.append(result['objects'])

        #     # Done retrieving data?
        #     if result['token'] is None:
        #         break

        #     print "Continuing (token=%s).." % result['token']
        #     result = yield client.makeRequest('VimPortType', 'continueRetrievePropertiesEx',
        #         prop_collector, result['token'])
        #   print json.dumps(all_objects, indent=4)

        #### WaitFoUpdatesEx version
        log.info("Installing propertyFilter for updates")
        result = yield client.makeRequest(
            'VimPortType', 'createFilter',
            prop_collector, prop_filter_spec, False)

        wait_options = {
            'maxObjectUpdates': 1000,
            'maxWaitSeconds': 120,
        }

        version = ''

        log.info("Retrieving updates (initial version)")
        result = yield client.makeRequest(
            'VimPortType', 'waitForUpdatesEx',
            prop_collector, version, wait_options)

        totalObjectUpdates = 0

        mapper = ApplyDataMap()

        # create our device
        device = self.dmd.Devices.findDevice(self.options.hostname)
        if device:
            device.deleteDevice()

        device = self.dmd.Devices.XenServer.createInstance(self.options.hostname)

        # these will get moved into the xenserver endpoint object, when I
        # get around to it.
        fullstate = VIFullState()
        incrstate = VIIncrState()

        while True:
            version = result['version']

            file = "/tmp/result_" + version + ".json"
            print "Writing " + file
            f = open(file, 'w')
            f.write(json.dumps(result, indent=4))
            f.close()

            # note that I assume only one filter is loaded.
            totalObjectUpdates += len(result['filterSet'][0]['objectSet'])
            log.info("  Processing %d updates." % len(result['filterSet'][0]['objectSet']))

            incrstate.cacheUpdateSets([result])
            fullstate.applyUpdateSets([result])

            if not result['truncated']:
                log.info("  Initial update is complete.  Processed %d objectUpdates" % totalObjectUpdates)
                break

            log.info("Continuing (version=%s).." % version)
            result = yield client.makeRequest(
                'VimPortType', 'waitForUpdatesEx',
                prop_collector, version, wait_options)

        processfullstate(
            service_content['rootFolder'],
            fullstate,
            incrstate,
            device,
            mapper)

        # done with this.
        del fullstate

        log.info("Initial model complete.  Waiting for updates.")

        while True:
            log.debug("Calling waitForUpdatesEx..")
            result = yield client.makeRequest(
                'VimPortType', 'waitForUpdatesEx',
                prop_collector, version, wait_options)

            if result is None:
                continue

            version = result['version']

            file = "/tmp/result_" + version + ".json"
            print "Writing " + file
            f = open(file, 'w')
            f.write(json.dumps(result, indent=4))
            f.close()

            # note that I assume only one filter is loaded.
            totalObjectUpdates += len(result['filterSet'][0]['objectSet'])
            log.info("  Processing %d updates." % len(result['filterSet'][0]['objectSet']))

            datamaps = incrstate.applyUpdateSets([result])
            try:
                for datamap in datamaps:
                    log.debug("Applying " + pformat(datamap))
                    mapper._applyDataMap(device, datamap)
            except Exception, e:
                log.error("Exception while processing incremental update:")
                log.exception(e)


        # perf_counters = yield getPerformanceCounters(client, service_content)
        # log.info("Performance counters: %s", perf_counters)



def processfullstate(root_folder_moid, fullstate, incrstate, device, mapper):
    from ZenPacks.zenoss.XenServer.Endpoint import Endpoint

    datamaps = Endpoint.containingDataMapsFullState(fullstate, incrstate, root_folder_moid)

    # # Process non-containing relationships (add to exising objmaps):
    # Endpoint.addNonContainingRelsFullState(fullstate, incrstate, root_folder_moid)

    # Try applying these maps.
    log.info("Applying %d DataMaps" % len(datamaps))

    for datamap in datamaps:
        log.debug("Applying " + pformat(datamap))
        mapper._applyDataMap(device, datamap)

    # Process non-containing relationships (add to exising objmaps):
    Endpoint.addNonContainingRelsFullState(fullstate, incrstate, root_folder_moid)
    datamaps.append(ObjectMap(data={"setRootFolder": moidToId(root_folder_moid)}))

    for datamap in datamaps:
        log.debug("Re-Applying " + pformat(datamap))
        mapper._applyDataMap(device, datamap)

    log.info("Committing.")
    transaction.commit()
    log.info("Done.")

    gvFile = deviceToGraphviz(device)
    print "Writing /tmp/graph.gv"
    f = open('/tmp/graph.gv', 'w')
    f.write(gvFile)
    f.close()


def getPerformanceCounters(protocol, service_content):
    prop_collector = service_content['propertyCollector']
    perf_manager = service_content['perfManager']
    prop_filter_spec = {
        'propSet': [
            {
                'type': perf_manager['type'],
                'all': False,
                'pathSet': ['perfCounter'],
            },
        ],
        'objectSet': [
            {
                'obj': perf_manager,
                'skip': False,
            },
        ]
    }

    return protocol.makeRequest(
        'VimPortType', 'retrieveProperties',
        prop_collector, [prop_filter_spec])


def main():
    from twisted.internet import reactor

    modeler = XenServerModeler(connect=True)
    modeler.verify_options()

    def finished(result):
        log.debug(result)
        reactor.stop()

    modeler.run().addBoth(finished)
    reactor.run()


if __name__ == '__main__':
    main()
