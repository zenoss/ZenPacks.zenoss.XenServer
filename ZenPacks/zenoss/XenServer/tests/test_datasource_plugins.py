##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from Products.ZenTestCase.BaseTestCase import BaseTestCase

from ZenPacks.zenoss.XenServer.datasource_plugins import aggregate_values


class Mock:
    pass


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
            datapoint.params = {
                'group_aggregation': group_f,
                'time_aggregation': time_f,
                }

            r = aggregate_values(datapoint, v)

            self.assertEquals(
                r, expected,
                "group {0} of time {1} for {2} was {3} instead of {4}".format(
                    group_f, time_f, v, r, expected))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUtils))
    return suite
