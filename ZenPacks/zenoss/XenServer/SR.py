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
    PooledComponent, IPooledComponentInfo, PooledComponentInfo,
    RelationshipLengthProperty,
    updateToMany,
    id_from_ref, ids_from_refs,
    )


class SR(PooledComponent):
    '''
    Model class for SR. Also known as Storage Repository.
    '''

    class_label = 'Storage Repository'
    class_plural_label = 'Storage Repositories'

    meta_type = portal_type = 'XenServerSR'

    allowed_operations = None
    content_type = None
    local_cache_enabled = None
    name_description = None
    name_label = None
    physical_size = None
    shared = None
    sm_type = None
    sr_type = None

    _properties = PooledComponent._properties + (
        {'id': 'allowed_operations', 'label': 'Allowed Operations', 'type': 'lines', 'mode': 'w'},
        {'id': 'content_type', 'label': 'Content Type', 'type': 'string', 'mode': 'w'},
        {'id': 'local_cache_enabled', 'label': 'Local Cache Enabled', 'type': 'boolean', 'mode': 'w'},
        {'id': 'name_description', 'label': 'Description', 'type': 'string', 'mode': 'w'},
        {'id': 'name_label', 'label': 'Label', 'type': 'string', 'mode': 'w'},
        {'id': 'physical_size', 'label': 'Physical Size', 'type': 'int', 'mode': 'w'},
        {'id': 'shared', 'label': 'Shared', 'type': 'boolean', 'mode': 'w'},
        {'id': 'sm_type', 'label': 'SM Type', 'type': 'string', 'mode': 'w'},
        {'id': 'sr_type', 'label': 'Type', 'type': 'string', 'mode': 'w'},
        )

    _relations = PooledComponent._relations + (
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

    @classmethod
    def objectmap(cls, ref, properties):
        '''
        Return an ObjectMap given XenAPI SR ref and properties.
        '''
        if 'uuid' not in properties:
            return {
                'relname': 'sr',
                'id': id_from_ref(ref),
                }

        title = properties.get('name_label') or properties['uuid']

        sm_config = properties.get('sm_config', {})

        return {
            'relname': 'srs',
            'id': id_from_ref(ref),
            'title': title,
            'xenapi_ref': ref,
            'xenapi_uuid': properties.get('uuid'),
            'allowed_operations': properties.get('allowed_operations'),
            'content_type': properties.get('content_type'),
            'local_cache_enabled': properties.get('local_cache_enabled'),
            'name_description': properties.get('name_description'),
            'name_label': properties.get('name_label'),
            'physical_size': properties.get('physical_size'),
            'shared': properties.get('shared'),
            'sm_type': sm_config.get('type'),
            'sr_type': properties.get('type'),
            'setPBDs': ids_from_refs(properties.get('PBDs', []))
            }

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

    def xenrrd_prefix(self):
        '''
        Return prefix under which XenServer stores RRD data about this
        component.
        '''
        # This is a guess at future support. XenServer 6.2 doesn't have
        # any RRD data for SRs.
        if self.xenapi_uuid:
            return ('sr', self.xenapi_uuid, '')

    def getIconPath(self):
        '''
        Return URL to icon representing objects of this class.
        '''
        return '/++resource++xenserver/img/storage-domain.png'


class ISRInfo(IPooledComponentInfo):
    '''
    API Info interface for SR.
    '''

    allowed_operations = schema.Text(title=_t(u'Allowed Operations'))
    content_type = schema.TextLine(title=_t(u'Content Type'))
    local_cache_enabled = schema.Bool(title=_t(u'Local Cache Enabled'))
    name_description = schema.TextLine(title=_t(u'Description'))
    name_label = schema.TextLine(title=_t(u'Label'))
    physical_size = schema.Int(title=_t(u'Physical Size'))
    shared = schema.Bool(title=_t(u'Shared'))
    sm_type = schema.TextLine(title=_t(u'SM Type'))
    sr_type = schema.TextLine(title=_t(u'Type'))

    vdi_count = schema.Int(title=_t(u'Number of VDIS'))
    pbd_count = schema.Int(title=_t(u'Number of PBDS'))


class SRInfo(PooledComponentInfo):
    '''
    API Info adapter factory for SR.
    '''

    implements(ISRInfo)
    adapts(SR)

    allowed_operations = ProxyProperty('allowed_operations')
    content_type = ProxyProperty('content_type')
    local_cache_enabled = ProxyProperty('local_cache_enabled')
    name_description = ProxyProperty('name_description')
    name_label = ProxyProperty('name_label')
    physical_size = ProxyProperty('physical_size')
    shared = ProxyProperty('shared')
    sm_type = ProxyProperty('sm_type')
    sr_type = ProxyProperty('sr_type')

    vdi_count = RelationshipLengthProperty('vdis')
    pbd_count = RelationshipLengthProperty('pbds')
