##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from ZenPacks.zenoss.XenServer import ZENPACK_NAME
from ZenPacks.zenoss.XenServer.utils import guid

# Lazy imports to make this module not require Impact.
ImpactEdge = None
Trigger = None

# Constants to avoid typos.
AVAILABILITY = 'AVAILABILITY'
PERCENT = 'policyPercentageTrigger'
THRESHOLD = 'policyThresholdTrigger'
DOWN = 'DOWN'
DEGRADED = 'DEGRADED'
ATRISK = 'ATRISK'


def edge(source, target):
    '''
    Create an edge indicating that source impacts target.

    source and target are expected to be GUIDs.
    '''
    # Lazy import without incurring import overhead.
    # http://wiki.python.org/moin/PythonSpeed/PerformanceTips#Import_Statement_Overhead
    global ImpactEdge
    if not ImpactEdge:
        from ZenPacks.zenoss.Impact.impactd.relations import ImpactEdge

    return ImpactEdge(source, target, ZENPACK_NAME)


class BaseImpactAdapterFactory(object):
    '''
    Abstract base for Impact adapter factories.
    '''

    def __init__(self, adapted):
        self.adapted = adapted

    def guid(self):
        if not hasattr(self, '_guid'):
            self._guid = guid(self.adapted)

        return self._guid


class BaseRelationsProvider(BaseImpactAdapterFactory):
    '''
    Abstract base for IRelationshipDataProvider adapter factories.
    '''

    relationship_provider = ZENPACK_NAME

    impact_relationships = None
    impacted_by_relationships = None

    def belongsInImpactGraph(self):
        return True

    def impact(self, relname):
        relationship = getattr(self.adapted, relname, None)
        if relationship and callable(relationship):
            related = relationship()
            if not related:
                return

            try:
                for obj in related:
                    yield edge(self.guid(), guid(obj))

            except TypeError:
                yield edge(self.guid(), guid(related))

    def impacted_by(self, relname):
        relationship = getattr(self.adapted, relname, None)
        if relationship and callable(relationship):
            related = relationship()
            if not related:
                return

            try:
                for obj in related:
                    yield edge(guid(obj), self.guid())

            except TypeError:
                yield edge(guid(related), self.guid())

    def getEdges(self):
        if self.impact_relationships is not None:
            for impact_relationship in self.impact_relationships:
                for impact in self.impact(impact_relationship):
                    yield impact

        if self.impacted_by_relationships is not None:
            for impacted_by_relationship in self.impacted_by_relationships:
                for impacted_by in self.impacted_by(impacted_by_relationship):
                    yield impacted_by


class BaseTriggers(BaseImpactAdapterFactory):
    '''
    Abstract base for INodeTriggers adapter factories.
    '''
    triggers = []

    def get_triggers(self):
        '''
        Return list of triggers defined by subclass' triggers property.
        '''
        # Lazy import without incurring import overhead.
        # http://wiki.python.org/moin/PythonSpeed/PerformanceTips#Import_Statement_Overhead
        global Trigger
        if not Trigger:
            from ZenPacks.zenoss.Impact.impactd import Trigger

        for trigger_args in self.triggers:
            yield Trigger(self.guid(), *trigger_args)


### XenServer Impact Providers ###############################################

class EndpointRelationsProvider(BaseRelationsProvider):
    impact_relationships = ('hosts',)


class HostRelationsProvider(BaseRelationsProvider):
    impacted_by_relationships = (
        'endpoint',
        'pbds',
        'pifs',
        'suspend_image_sr',
        'crash_dump_sr',
        'local_cache_sr',
        'server_device',
        )

    impact_relationships = ('pool', 'vms', 'cloudstack_host')


class NetworkRelationsProvider(BaseRelationsProvider):
    impacted_by_relationships = ('pifs',)
    impact_relationships = ('vifs',)


class PBDRelationsProvider(BaseRelationsProvider):
    impacted_by_relationships = ('server_disk',)
    impact_relationships = ('sr', 'host')


class PIFRelationsProvider(BaseRelationsProvider):
    impacted_by_relationships = ('server_interface',)
    impact_relationships = ('network', 'host')


class PoolRelationsProvider(BaseRelationsProvider):
    impacted_by_relationships = (
        'hosts',
        'default_sr',
        'suspend_image_sr',
        'crash_dump_sr',
        )

    impact_relationships = ('vms',)


class SRRelationsProvider(BaseRelationsProvider):
    impacted_by_relationships = ('pbds',)
    impact_relationships = (
        'vdis',
        'suspend_image_for_hosts',
        'crash_dump_for_hosts',
        'local_cache_for_hosts',
        'default_for_pools',
        'suspend_image_for_pools',
        'crash_dump_for_pools',
        )


class VBDRelationsProvider(BaseRelationsProvider):
    impacted_by_relationships = ('vdi',)
    impact_relationships = ('vms', 'guest_disk')


class VDIRelationsProvider(BaseRelationsProvider):
    impacted_by_relationships = ('sr',)
    impact_relationships = ('vbds',)


class VIFRelationsProvider(BaseRelationsProvider):
    impacted_by_relationships = ('network',)
    impact_relationships = ('vm', 'guest_interface')


class VMRelationsProvider(BaseRelationsProvider):
    impacted_by_relationships = ('host', 'pool', 'vbds', 'vifs')
    impact_relationships = (
        'vmappliances',
        'guest_device',
        'cloudstack_routervm',
        'cloudstack_systemvm',
        'cloudstack_vm',
        )


class VMApplianceRelationsProvider(BaseRelationsProvider):
    impacted_by_relationships = ('vms',)


### Platform Impact Providers ################################################

class DeviceRelationsProvider(BaseRelationsProvider):
    impacted_by_relationships = ('xenserver_vm',)
    impact_relationships = ('xenserver_host',)


class HardDiskRelationsProvider(BaseRelationsProvider):
    impacted_by_relationships = ('xenserver_vbd',)
    impact_relationships = ('xenserver_pbd',)


class IpInterfaceRelationsProvider(BaseRelationsProvider):
    impacted_by_relationships = ('xenserver_vif',)
    impact_relationships = ('xenserver_pif',)
