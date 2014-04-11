##############################################################################
#
# Copyright (C) Zenoss, Inc. 2014, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Unit tests for invalidation processing."""

from Products.ZenHub.interfaces import FILTER_CONTINUE, FILTER_EXCLUDE, FILTER_INCLUDE
from Products.ZenTestCase.BaseTestCase import BaseTestCase

from .utils import create_endpoint


def filtername(value):
    """Return name of filter given int value."""
    return {
        FILTER_EXCLUDE: 'EXCLUDE',
        FILTER_INCLUDE: 'INCLUDE',
        FILTER_CONTINUE: 'CONTINUE',
        }.get(value, 'INVALID')


class TestInvalidations(BaseTestCase):

    """Test suite for ZenHub invalidation processing."""

    def afterSetUp(self):
        super(TestInvalidations, self).afterSetUp()

        # Create the endpoint before initializing invalidation filter.
        self.endpoint()

        # Initialize invalidation filter.
        from ..invalidations import InvalidationFilter

        self.filter = InvalidationFilter()
        self.filter.initialize(self.dmd)

    def endpoint(self):
        """Return an endpoint suitable for testing."""
        if not hasattr(self, '_endpoint'):
            self._endpoint = create_endpoint(self.dmd)

        return self._endpoint

    def assertFilter(self, obj, expected, format_string):
        """Assert filter result for obj equals expected."""
        if not format_string:
            format_string = "result is {result} instead of {expected}"

        result = self.filter.include(obj)

        self.assertTrue(
            result == expected,
            format_string.format(
                result=filtername(result),
                expected=filtername(expected)))

    def test_Endpoint_invalidations(self):
        endpoint = self.endpoint()
        self.assertFilter(
            endpoint, FILTER_EXCLUDE,
            "Endpoint: initial result is {result} instead of {expected}")

        # Change things that shouldn't result in invalidation.
        endpoint.setZenProperty('zSnmpCommunity', 'nomatter')
        self.assertFilter(
            endpoint, FILTER_EXCLUDE,
            "Endpoint.zSnmpComunity result is {result} instead of {expected}")

        # Change things that should result in invalidation.
        endpoint.productionState = -1
        self.assertFilter(
            endpoint, FILTER_CONTINUE,
            "Endpoint.monitorDevice() result is {result} instead of {expected}")

        # Reset productionState.
        endpoint.productionState = 1000
        self.filter.include(endpoint)

        endpoint.setZenProperty('zXenServerPerfInterval', 10)
        self.assertFilter(
            endpoint, FILTER_CONTINUE,
            "Endpoint.zXenServerPerfInterval result is {result} instead of {expected}")

    def test_Host_invalidations(self):
        host = self.endpoint().hosts()[0]

        self.assertFilter(
            host, FILTER_EXCLUDE,
            "Host: initial result is {result} instead of {expected}")

        # Change things that shouldn't result in invalidation.
        host.cpu_count = 24
        self.assertFilter(
            host, FILTER_EXCLUDE,
            "Host.cpu_count result is {result} instead of {expected}")

        host.cpu_speed = 2800.0
        self.assertFilter(
            host, FILTER_EXCLUDE,
            "Host.cpu_speed result is {result} instead of {expected}")

        # Change things that should result in invalidation.
        host.monitor = False
        self.assertFilter(
            host, FILTER_CONTINUE,
            "Host.monitored() result is {result} instead of {expected}")


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInvalidations))
    return suite
