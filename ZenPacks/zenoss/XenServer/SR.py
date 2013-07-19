######################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is
# installed.
#
######################################################################

from zope.component import adapts
from zope.interface import implements

from Products.ZenRelations.RelSchema import ToMany, ToManyCont, ToOne
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.utils import ZuulMessageFactory as _t

from ZenPacks.zenoss.XenServer import CLASS_NAME, MODULE_NAME
from ZenPacks.zenoss.XenServer.utils import (
    BaseComponent, IBaseComponentInfo, BaseComponentInfo,
    RelationshipLengthProperty,
    updateToMany,
    )


class SR(BaseComponent):
    '''
    Model class for SR. Also known as Storage Repository.
    '''

    meta_type = portal_type = 'XenServerSR'

    name_label = None
    name_description = None
    physical_size = None
    physical_utilisation = None
    content_type = None
    shared = None
    virtual_allocation = None

    _properties = BaseComponent._properties + (
        {'id': 'name_label', 'type': 'string', 'mode': 'w'},
        {'id': 'name_description', 'type': 'string', 'mode': 'w'},
        {'id': 'physical_size', 'type': 'string', 'mode': 'w'},
        {'id': 'physical_utilisation', 'type': 'string', 'mode': 'w'},
        {'id': 'content_type', 'type': 'string', 'mode': 'w'},
        {'id': 'shared', 'type': 'string', 'mode': 'w'},
        {'id': 'virtual_allocation', 'type': 'string', 'mode': 'w'},
        )

    _relations = BaseComponent._relations + (
        ('endpoint', ToOne(ToManyCont, MODULE_NAME['Endpoint'], 'srs',)),
        ('vdis', ToManyCont(ToOne, MODULE_NAME['VDI'], 'sr',)),
        ('pbds', ToMany(ToOne, MODULE_NAME['PBD'], 'sr',)),
        ('default_for_pools', ToMany(ToOne, MODULE_NAME['Pool'], 'default_sr')),
        ('suspend_image_for_pools', ToMany(ToOne, MODULE_NAME['Pool'], 'suspend_image_sr')),
        ('crash_dump_for_pools', ToMany(ToOne, MODULE_NAME['Pool'], 'crash_dump_sr')),
        ('suspend_image_for_hosts', ToMany(ToOne, MODULE_NAME['Host'], 'suspend_image_sr')),
        ('crash_dump_for_hosts', ToMany(ToOne, MODULE_NAME['Host'], 'crash_dump_sr')),
        ('local_cache_for_hosts', ToMany(ToOne, MODULE_NAME['Host'], 'local_cache_sr')),
        )

    def getPBDs(self):
        '''
        Return a sorted list of related PBD ids.

        Used by modeling.
        '''
        return sorted(x.id for x in self.pbds.objectValuesGen())

    def setPBDs(self, pbd_ids):
        '''
        Update PBD relationship given PBD ids.

        Used by modeling.
        '''
        updateToMany(
            relationship=self.pbds,
            root=self.device(),
            type_=CLASS_NAME['PBD'],
            ids=pbd_ids)

    def getDefaultForPools(self):
        '''
        Return a sorted list of related Pool ids.

        Used by modeling.
        '''
        return sorted(x.id for x in self.default_for_pools.objectValuesGen())

    def setDefaultForPools(self, pool_ids):
        '''
        Set default_for_pools relationship by Pool id.

        Used by modeling.
        '''
        updateToMany(
            relationship=self.default_for_pools,
            root=self.device(),
            type_=CLASS_NAME['Pool'],
            ids=pool_ids)

    def getSuspendImageForPools(self):
        '''
        Return a sorted list of related Pool ids.

        Used by modeling.
        '''
        return sorted(x.id for x in self.suspend_image_for_pools.objectValuesGen())

    def setSuspendImageForPools(self, pool_ids):
        '''
        Set suspend_image_for_pools relationship by Pool id.

        Used by modeling.
        '''
        updateToMany(
            relationship=self.suspend_image_for_pools,
            root=self.device(),
            type_=CLASS_NAME['Pool'],
            ids=pool_ids)

    def getCrashDumpForPools(self):
        '''
        Return a sorted list of related Pool ids.

        Used by modeling.
        '''
        return sorted(x.id for x in self.crash_dump_for_pools.objectValuesGen())

    def setCrashDumpForPools(self, pool_ids):
        '''
        Set crash_dump_for_pools relationship by Pool id.

        Used by modeling.
        '''
        updateToMany(
            relationship=self.crash_dump_for_pools,
            root=self.device(),
            type_=CLASS_NAME['Pool'],
            ids=pool_ids)

    def getSuspendImageForHosts(self):
        '''
        Return a sorted list of related Host ids.

        Used by modeling.
        '''
        return sorted(x.id for x in self.suspend_image_for_hosts.objectValuesGen())

    def setSuspendImageForHosts(self, pool_ids):
        '''
        Set suspend_image_for_hosts relationship by Host id.

        Used by modeling.
        '''
        updateToMany(
            relationship=self.suspend_image_for_hosts,
            root=self.device(),
            type_=CLASS_NAME['Host'],
            ids=pool_ids)

    def getCrashDumpForHosts(self):
        '''
        Return a sorted list of related Host ids.

        Used by modeling.
        '''
        return sorted(x.id for x in self.crash_dump_for_hosts.objectValuesGen())

    def setCrashDumpForHosts(self, pool_ids):
        '''
        Set crash_dump_for_hosts relationship by Host id.

        Used by modeling.
        '''
        updateToMany(
            relationship=self.crash_dump_for_hosts,
            root=self.device(),
            type_=CLASS_NAME['Host'],
            ids=pool_ids)

    def getLocalCacheForHosts(self):
        '''
        Return a sorted list of related Host ids.

        Used by modeling.
        '''
        return sorted(x.id for x in self.local_cache_for_hosts.objectValuesGen())

    def setLocalCacheForHosts(self, pool_ids):
        '''
        Set local_cache_for_hosts relationship by Host id.

        Used by modeling.
        '''
        updateToMany(
            relationship=self.local_cache_for_hosts,
            root=self.device(),
            type_=CLASS_NAME['Host'],
            ids=pool_ids)


class ISRInfo(IBaseComponentInfo):
    '''
    API Info interface for SR.
    '''

    name_label = schema.TextLine(title=_t(u'name_labels'))
    name_description = schema.TextLine(title=_t(u'name_descriptions'))
    physical_size = schema.TextLine(title=_t(u'physical_sizes'))
    physical_utilisation = schema.TextLine(title=_t(u'physical_utilisations'))
    content_type = schema.TextLine(title=_t(u'content_types'))
    shared = schema.TextLine(title=_t(u'shareds'))
    virtual_allocation = schema.TextLine(title=_t(u'virtual_allocations'))

    vdi_count = schema.Int(title=_t(u'Number of VDIS'))
    pbd_count = schema.Int(title=_t(u'Number of PBDS'))


class SRInfo(BaseComponentInfo):
    '''
    API Info adapter factory for SR.
    '''

    implements(ISRInfo)
    adapts(SR)

    name_label = ProxyProperty('name_label')
    name_description = ProxyProperty('name_description')
    physical_size = ProxyProperty('physical_size')
    physical_utilisation = ProxyProperty('physical_utilisation')
    content_type = ProxyProperty('content_type')
    shared = ProxyProperty('shared')
    virtual_allocation = ProxyProperty('virtual_allocation')

    vdi_count = RelationshipLengthProperty('vdis')
    pbd_count = RelationshipLengthProperty('pbds')
