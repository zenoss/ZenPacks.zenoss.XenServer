##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from Products.ZenTestCase.BaseTestCase import BaseTestCase

from ZenPacks.zenoss.XenServer.datasource_plugins import aggregate_values, XenAPIPlugin, XenAPIEventsPlugin, XenAPIMessagesPlugin, XenRRDPlugin

class CollectXenException(Exception):
    """
    Exception raised by test TestXenApi used to test that it is called
    """

class Mock:
    pass

class mockConfig:
    id = 'testID'
    datasources = []
    
class mockDatasource:
    xenserver_addresses = ['192.20.102.104']
    zXenServerPassword = 'testUser'
    zXenServerUsername = 'testPass'
    params = {'xenapi_classname': 'host'}

class TestXenAPIPlugin(XenAPIPlugin):
    def collect_xen(self, config, ds0, client):
        self.onError('testPlugin', config)
        raise CollectXenException()

class TestXenAPIEventsPlugin(XenAPIEventsPlugin):
    def collect_xen(self, config, ds0, client):
        self.onError('testEventsPlugin', config)
        raise CollectXenException()
        
class TestXenAPIMessagesPlugin(XenAPIMessagesPlugin):
    def collect_xen(self, config, ds0, client):
        self.onError('testMessagesPlugin', config)
        raise CollectXenException()

class TestXenRRDPlugin(XenRRDPlugin):
    def collect_xen(self, config, ds0, client):
        self.onError('testRRDPlugin', config)
        raise CollectXenException()
        
class TestUtils(BaseTestCase):
    def test_aggregate_values(self):
        values = [
            [1.0, 2.0, 3.0, 4.0],
            [5.0, 6.0, 7.0, 8.0],
        ]

        cases = [
            # Time aggregations.
            ('AVERAGE', 'MIN', values[0:1], 1.0),
            ('AVERAGE', 'AVERAGE', values[0:1], 2.5),
            ('AVERAGE', 'MAX', values[0:1], 4.0),
            ('AVERAGE', 'SUM', values[0:1], 10.0),

            # Group min aggregations.
            ('MIN', 'MIN', values, 1.0),
            ('MIN', 'AVERAGE', values, 2.5),
            ('MIN', 'MAX', values, 4.0),
            ('MIN', 'SUM', values, 10.0),

            # Group average aggregations.
            ('AVERAGE', 'MIN', values, 3.0),
            ('AVERAGE', 'AVERAGE', values, 4.5),
            ('AVERAGE', 'MAX', values, 6.0),
            ('AVERAGE', 'SUM', values, 18.0),

            # Group max aggregations.
            ('MAX', 'MIN', values, 5.0),
            ('MAX', 'AVERAGE', values, 6.5),
            ('MAX', 'MAX', values, 8.0),
            ('MAX', 'SUM', values, 26.0),

            # Group sum aggregations.
            ('SUM', 'MIN', values, 6.0),
            ('SUM', 'AVERAGE', values, 9.0),
            ('SUM', 'MAX', values, 12.0),
            ('SUM', 'SUM', values, 36.0),
        ]

        for group_f, time_f, v, expected in cases:
            datapoint = Mock()
            datapoint.group_aggregation = group_f
            datapoint.time_aggregation = time_f
            # datapoint.params = {
            #     'group_aggregation': group_f,
            #     'time_aggregation': time_f,
            #     }

            r = aggregate_values(datapoint, v)

            self.assertEquals(
                r, expected,
                "group {0} of time {1} for {2} was {3} instead of {4}".format(
                    group_f, time_f, v, r, expected))
                    
    def test_client_cache_removal(self):
        #classes being tested for client cache removal on Error
        self.xenApiPlugin = TestXenAPIPlugin()
        self.xenApiEventsPlugin = TestXenAPIEventsPlugin()
        self.xenApiMessagesPlugin = TestXenAPIMessagesPlugin()
        self.xenRRDPlugin = TestXenRRDPlugin()
        #generate test config
        ds0 = mockDatasource()
        config = mockConfig()
        config.datasources = [ds0]
        
        with self.assertRaises(CollectXenException):
            self.xenApiPlugin.collect(config)
            
        with self.assertRaises(CollectXenException):
            self.xenApiEventsPlugin.collect(config)
            
        with self.assertRaises(CollectXenException):
            self.xenApiMessagesPlugin.collect(config)
            
        with self.assertRaises(CollectXenException):
            self.xenRRDPlugin.collect(config)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUtils))
    return suite
