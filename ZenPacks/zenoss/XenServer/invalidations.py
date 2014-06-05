##############################################################################
#
# Copyright (C) Zenoss, Inc. 2014, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""ZenHub invalidation processing."""

import logging
LOG = logging.getLogger('zen.XenServer')

import hashlib

from zope.interface import implements

from Products.ZenHub.interfaces import IInvalidationFilter
from Products.ZenHub.interfaces import FILTER_CONTINUE, FILTER_EXCLUDE
from Products.Zuul.interfaces import ICatalogTool

from .Endpoint import Endpoint
from .Host import Host
from .HostCPU import HostCPU
from .Network import Network
from .PBD import PBD
from .PIF import PIF
from .Pool import Pool
from .SR import SR
from .VBD import VBD
from .VDI import VDI
from .VIF import VIF
from .VM import VM
from .VMAppliance import VMAppliance


class Checksummer(object):

    """Defines and executes checksum of an object."""

    def __init__(self, zProperties=(), properties=(), methods=()):
        self.zProperties = zProperties
        self.properties = properties
        self.methods = methods

    def __call__(self, obj):
        """Return MD5 hexdigest checksum for obj."""
        m = hashlib.md5()

        for zProp in self.zProperties:
            m.update('{}={}'.format(zProp, obj.getZ(zProp)))

        for prop in self.properties:
            m.update('{}={}'.format(prop, getattr(obj, prop, None)))

        for methodname in self.methods:
            method = getattr(obj, methodname, None)
            if method and callable(method):
                m.update('{}={}'.format(methodname, method()))

        return m.hexdigest()

EndpointChecksummer = Checksummer(
    zProperties=(
        'zXenServerUsername',
        'zXenServerPassword',
        'zXenServerPerfInterval',
        'zXenServerModelInterval',
        'zXenServerEventsInterval',
        ),
    properties=(
        'xenserver_addresses',
        ),
    methods=(
        'monitorDevice',
        ),
    )

ComponentChecksummer = Checksummer(
    methods=(
        'monitored',
        'xenapi_ref',
        'xenapi_metrics_ref',
        'xenapi_guest_metrics_ref',
        'xenrrd_prefix',
        ),
    )

# Specification of which classes to checksum and how to do it.
CHECKSUMMERS = {
    Endpoint: EndpointChecksummer,

    Host: ComponentChecksummer,
    HostCPU: ComponentChecksummer,
    Network: ComponentChecksummer,
    PBD: ComponentChecksummer,
    PIF: ComponentChecksummer,
    Pool: ComponentChecksummer,
    SR: ComponentChecksummer,
    VBD: ComponentChecksummer,
    VDI: ComponentChecksummer,
    VIF: ComponentChecksummer,
    VM: ComponentChecksummer,
    VMAppliance: ComponentChecksummer,
    }


def checksum(obj):
    """Return invalidation checksum for obj.

    Will return None if obj's class is not registered in CHECKSUMMERS.

    """
    obj_class = obj.__class__
    checksummer = CHECKSUMMERS.get(obj_class)
    if checksummer:
        return checksummer(obj)


class InvalidationFilter(object):

    """InvalidationFilter for all objects of this ZenPack.

    Excludes invalidations that shouldn't result in any change in
    monitoring.

    """

    implements(IInvalidationFilter)

    weight = 0

    def initialize(self, context):
        LOG.debug("initializing invalidation checksums")
        catalog = ICatalogTool(context.dmd.Devices.primaryAq())
        self.checksums = {}
        for b in catalog.search(CHECKSUMMERS.keys()):
            try:
                self.checksums[b.getPath()] = checksum(b.getObject())
            except Exception:
                # Catalog or database inconsistencies must not prevent
                # zenhub from starting.
                pass

        LOG.debug("initialized %d invalidation checksums", len(self.checksums))

    def include(self, obj):
        obj_class = obj.__class__
        if obj_class not in CHECKSUMMERS:
            # No custom filtering for invalidations of this class.
            return FILTER_CONTINUE

        obj_path = obj.getPrimaryUrlPath()
        new_checksum = checksum(obj)
        old_checksum = self.checksums.get(obj_path)
        if new_checksum != old_checksum:
            self.checksums[obj_path] = new_checksum
            LOG.debug(
                "invalidation checksum change for %s: %s",
                obj_class.__name__,
                obj.id)

            return FILTER_CONTINUE

        # Invalidation checksum hasn't changed.
        return FILTER_EXCLUDE
