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
    RelationshipInfoProperty, RelationshipLengthProperty,
    updateToMany, updateToOne,
    )


class Host(BaseComponent):
    '''
    Model class for Host. Also known as Server.
    '''

    meta_type = portal_type = 'XenServerHost'

    name_label = None
    name_description = None
    address = None

    _properties = BaseComponent._properties + (
        {'id': 'name_label', 'type': 'string', 'mode': 'w'},
        {'id': 'name_description', 'type': 'string', 'mode': 'w'},
        {'id': 'address', 'type': 'string', 'mode': 'w'},
        )

    _relations = BaseComponent._relations + (
        ('endpoint', ToOne(ToManyCont, MODULE_NAME['Endpoint'], 'hosts')),
        ('hostcpus', ToManyCont(ToOne, MODULE_NAME['HostCPU'], 'host')),
        ('pbds', ToManyCont(ToOne, MODULE_NAME['PBD'], 'host')),
        ('pifs', ToManyCont(ToOne, MODULE_NAME['PIF'], 'host')),
        ('vms', ToMany(ToOne, MODULE_NAME['VM'], 'host')),
        ('master_for', ToOne(ToOne, MODULE_NAME['Pool'], 'master')),
        ('suspend_image_sr', ToOne(ToMany, MODULE_NAME['SR'], 'suspend_image_for_hosts')),
        ('crash_dump_sr', ToOne(ToMany, MODULE_NAME['SR'], 'crash_dump_for_hosts')),
        ('local_cache_sr', ToOne(ToMany, MODULE_NAME['SR'], 'local_cache_for_hosts')),
        )

    def getVMs(self):
        '''
        Return a sorted list of each vm id related to this host.

        Used by modeling.
        '''

        return sorted(vm.id for vm in self.vms.objectValuesGen())

    def setVMs(self, vm_ids):
        '''
        Update VM relationship given ids.

        Used by modeling.
        '''
        updateToMany(
            relationship=self.vms,
            root=self.device(),
            type_=CLASS_NAME['VM'],
            ids=vm_ids)

    def getMasterFor(self):
        '''
        Return Pool id or None.

        Used by modeling.
        '''
        master_for = self.master_for()
        if master_for:
            return master_for.id

    def setMasterFor(self, pool_id):
        '''
        Set master_for relationship by Pool id.

        Used by modeling.
        '''
        updateToOne(
            relationship=self.master_for,
            root=self.device(),
            type_=CLASS_NAME['Pool'],
            id_=pool_id)

    def getSuspendImageSR(self):
        '''
        Return SR id or None.

        Used by modeling.
        '''
        suspend_image_sr = self.suspend_image_sr()
        if suspend_image_sr:
            return suspend_image_sr.id

    def setSuspendImageSR(self, sr_id):
        '''
        Set suspend_image_sr relationship by SR id.

        Used by modeling.
        '''
        updateToOne(
            relationship=self.suspend_image_sr,
            root=self.device(),
            type_=CLASS_NAME['SR'],
            id_=sr_id)

    def getCrashDumpSR(self):
        '''
        Return SR id or None.

        Used by modeling.
        '''
        crash_dump_sr = self.crash_dump_sr()
        if crash_dump_sr:
            return crash_dump_sr.id

    def setCrashDumpSR(self, sr_id):
        '''
        Set crash_dump_sr relationship by SR id.

        Used by modeling.
        '''
        updateToOne(
            relationship=self.crash_dump_sr,
            root=self.device(),
            type_=CLASS_NAME['SR'],
            id_=sr_id)

    def getLocalCacheSR(self):
        '''
        Return SR id or None.

        Used by modeling.
        '''
        local_cache_sr = self.local_cache_sr()
        if local_cache_sr:
            return local_cache_sr.id

    def setLocalCacheSR(self, sr_id):
        '''
        Set local_cache_sr relationship by SR id.

        Used by modeling.
        '''
        updateToOne(
            relationship=self.local_cache_sr,
            root=self.device(),
            type_=CLASS_NAME['SR'],
            id_=sr_id)


class IHostInfo(IBaseComponentInfo):
    '''
    API Info interface for Host.
    '''

    name_label = schema.TextLine(title=_t(u'Name'))
    name_description = schema.TextLine(title=_t(u'Description'))
    address = schema.TextLine(title=_t(u'Address'))

    master_for = schema.Entity(title=_t(u'Master for Pool'))
    suspend_image_sr = schema.Entity(title=_t(u'Suspend Image Storage Repository'))
    crash_dump_sr = schema.Entity(title=_t(u'Crash Dump Storage Repository'))
    local_cache_sr = schema.Entity(title=_t(u'Local Cache Storage Repository'))

    hostcpu_count = schema.Int(title=_t(u'Number of CPUs'))
    pbd_count = schema.Int(title=_t(u'Number of PBDs'))
    pif_count = schema.Int(title=_t(u'Number of PIFs'))
    vm_count = schema.Int(title=_t(u'Number of VMs'))


class HostInfo(BaseComponentInfo):
    '''
    API Info adapter factory for Host.
    '''

    implements(IHostInfo)
    adapts(Host)

    name_label = ProxyProperty('name_label')
    name_description = ProxyProperty('name_description')
    address = ProxyProperty('address')

    master_for = RelationshipInfoProperty('master_for')
    suspend_image_sr = RelationshipInfoProperty('suspend_image_sr')
    crash_dump_sr = RelationshipInfoProperty('crash_dump_sr')
    local_cache_sr = RelationshipInfoProperty('local_cache_sr')

    hostcpu_count = RelationshipLengthProperty('hostcpus')
    pbd_count = RelationshipLengthProperty('pbds')
    pif_count = RelationshipLengthProperty('pifs')
    vm_count = RelationshipLengthProperty('vms')
