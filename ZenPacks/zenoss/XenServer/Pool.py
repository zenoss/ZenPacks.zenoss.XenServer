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
    RelationshipInfoProperty,
    updateToOne,
    )


class Pool(BaseComponent):
    '''
    Model class for Pool.
    '''

    meta_type = portal_type = 'XenServerPool'

    ha_allow_overcommit = None
    ha_enabled = None
    ha_host_failures_to_tolerate = None
    name_description = None
    name_label = None
    oc_cpuid_feature_mask = None
    oc_memory_ratio_hvm = None
    oc_memory_ratio_pv = None
    vswitch_controller = None

    _properties = BaseComponent._properties + (
        {'id': 'ha_allow_overcommit', 'type': 'bool', 'mode': 'w'},
        {'id': 'ha_enabled', 'type': 'bool', 'mode': 'w'},
        {'id': 'ha_host_failures_to_tolerate', 'type': 'int', 'mode': 'w'},
        {'id': 'name_description', 'type': 'string', 'mode': 'w'},
        {'id': 'name_label', 'type': 'string', 'mode': 'w'},
        {'id': 'oc_cpuid_feature_mask', 'type': 'string', 'mode': 'w'},
        {'id': 'oc_memory_ratio_hvm', 'type': 'string', 'mode': 'w'},
        {'id': 'oc_memory_ratio_pv', 'type': 'string', 'mode': 'w'},
        {'id': 'vswitch_controller', 'type': 'string', 'mode': 'w'},
        )

    _relations = BaseComponent._relations + (
        ('endpoint', ToOne(ToManyCont, MODULE_NAME['Endpoint'], 'pools',)),
        ('master', ToOne(ToOne, MODULE_NAME['Host'], 'master_for')),
        ('default_sr', ToOne(ToMany, MODULE_NAME['SR'], 'default_for_pools')),
        ('suspend_image_sr', ToOne(ToMany, MODULE_NAME['SR'], 'suspend_image_for_pools')),
        ('crash_dump_sr', ToOne(ToMany, MODULE_NAME['SR'], 'crash_dump_for_pools')),
        )

    def getMaster(self):
        '''
        Return Host id or None.

        Used by modeling.
        '''
        master = self.master()
        if master:
            return master.id

    def setMaster(self, host_id):
        '''
        Set master relationship by host id.

        Used by modeling.
        '''
        updateToOne(
            relationship=self.master,
            root=self.device(),
            type_=CLASS_NAME['Host'],
            id_=host_id)

    def getDefaultSR(self):
        '''
        Return SR id or None.

        Used by modeling.
        '''
        default_sr = self.default_sr()
        if default_sr:
            return default_sr.id

    def setDefaultSR(self, sr_id):
        '''
        Set default_sr relationship by SR id.

        Used by modeling.
        '''
        updateToOne(
            relationship=self.default_sr,
            root=self.device(),
            type_=CLASS_NAME['SR'],
            id_=sr_id)

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


class IPoolInfo(IBaseComponentInfo):
    '''
    API Info interface for Pool.
    '''

    master = schema.Entity(title=_t(u'Master Host'))
    default_sr = schema.Entity(title=_t(u'Default Storage Repository'))
    suspend_image_sr = schema.Entity(title=_t(u'Suspend Image Storage Repository'))
    crash_dump_sr = schema.Entity(title=_t(u'Crash Dump Storage Repository'))

    ha_allow_overcommit = schema.Bool(title=_t(u'HA Allow Overcommit'))
    ha_enabled = schema.Bool(title=_t(u'HA Enabled'))
    ha_host_failures_to_tolerate = schema.Int(title=_t(u'HA Host Failures to Tolerate'))
    oc_cpuid_feature_mask = schema.TextLine(title=_t(u'CPU ID Feature Mask'))
    oc_memory_ratio_hvm = schema.TextLine(title=_t(u'HVM Memory Ratio'))
    oc_memory_ratio_pv = schema.TextLine(title=_t(u'PV Memory Ratio'))
    name_description = schema.TextLine(title=_t(u'Description'))
    name_label = schema.TextLine(title=_t(u'Label'))
    vswitch_controller = schema.TextLine(title=_t(u'vSwitch Controller'))


class PoolInfo(BaseComponentInfo):
    '''
    API Info adapter factory for Pool.
    '''

    implements(IPoolInfo)
    adapts(Pool)

    master = RelationshipInfoProperty('master')
    default_sr = RelationshipInfoProperty('default_sr')
    suspend_image_sr = RelationshipInfoProperty('suspend_image_sr')
    crash_dump_sr = RelationshipInfoProperty('crash_dump_sr')

    ha_allow_overcommit = ProxyProperty('ha_allow_overcommit')
    ha_enabled = ProxyProperty('ha_enabled')
    ha_host_failures_to_tolerate = ProxyProperty('ha_host_failures_to_tolerate')
    name_description = ProxyProperty('name_description')
    name_label = ProxyProperty('name_label')
    oc_cpuid_feature_mask = ProxyProperty('oc_cpuid_feature_mask')
    oc_memory_ratio_hvm = ProxyProperty('oc_memory_ratio_hvm')
    oc_memory_ratio_pv = ProxyProperty('oc_memory_ratio_pv')
    vswitch_controller = ProxyProperty('vswitch_controller')
