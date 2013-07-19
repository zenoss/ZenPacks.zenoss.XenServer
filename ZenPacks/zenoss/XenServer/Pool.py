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
    updateToOne,
    )


class Pool(BaseComponent):
    '''
    Model class for Pool.
    '''

    meta_type = portal_type = 'XenServerPool'

    name_label = None
    name_description = None
    vswitch_controller = None
    ha_enabled = None
    ha_plan_exists_for = None
    ha_allow_overcommit = None
    ha_host_failures_to_tolerate = None
    ha_overcommitted = None
    redo_log_enabled = None

    _properties = BaseComponent._properties + (
        {'id': 'name_label', 'type': 'string', 'mode': 'w'},
        {'id': 'name_description', 'type': 'string', 'mode': 'w'},
        {'id': 'vswitch_controller', 'type': 'string', 'mode': 'w'},
        {'id': 'ha_enabled', 'type': 'bool', 'mode': 'w'},
        {'id': 'ha_plan_exists_for', 'type': 'int', 'mode': 'w'},
        {'id': 'ha_allow_overcommit', 'type': 'bool', 'mode': 'w'},
        {'id': 'ha_host_failures_to_tolerate', 'type': 'int', 'mode': 'w'},
        {'id': 'ha_overcommitted', 'type': 'bool', 'mode': 'w'},
        {'id': 'redo_log_enabled', 'type': 'bool', 'mode': 'w'},
        )

    _relations = BaseComponent._relations + (
        ('endpoint', ToOne(ToManyCont, MODULE_NAME['Endpoint'], 'pools',)),
        ('master', ToOne(ToOne, MODULE_NAME['Host'], 'master_for')),
        ('default_sr', ToOne(ToMany, MODULE_NAME['SR'], 'default_for')),
        ('suspend_image_sr', ToOne(ToMany, MODULE_NAME['SR'], 'suspend_image_for')),
        ('crash_dump_sr', ToOne(ToMany, MODULE_NAME['SR'], 'crash_dump_for')),
        )

    def getMaster(self):
        '''
        Return Host id or None.

        Used by modeling.
        '''
        master = self.master()
        if master:
            return master

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
            return default_sr

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
            return suspend_image_sr

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
            return crash_dump_sr

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

    name_label = schema.TextLine(title=_t(u'name_labels'))
    name_description = schema.TextLine(title=_t(u'name_descriptions'))
    vswitch_controller = schema.TextLine(title=_t(u'vswitch_controllers'))
    ha_enabled = schema.Bool(title=_t(u'ha_enableds'))
    ha_plan_exists_for = schema.Int(title=_t(u'ha_plan_exists_fors'))
    ha_allow_overcommit = schema.Bool(title=_t(u'ha_allow_overcommits'))
    ha_host_failures_to_tolerate = schema.Int(title=_t(u'ha_host_failures_to_tolerates'))
    ha_overcommitted = schema.Bool(title=_t(u'ha_overcommitteds'))
    redo_log_enabled = schema.Bool(title=_t(u'redo_log_enableds'))


class PoolInfo(BaseComponentInfo):
    '''
    API Info adapter factory for Pool.
    '''

    implements(IPoolInfo)
    adapts(Pool)

    name_label = ProxyProperty('name_label')
    name_description = ProxyProperty('name_description')
    vswitch_controller = ProxyProperty('vswitch_controller')
    ha_enabled = ProxyProperty('ha_enabled')
    ha_plan_exists_for = ProxyProperty('ha_plan_exists_for')
    ha_allow_overcommit = ProxyProperty('ha_allow_overcommit')
    ha_host_failures_to_tolerate = ProxyProperty('ha_host_failures_to_tolerate')
    ha_overcommitted = ProxyProperty('ha_overcommitted')
    redo_log_enabled = ProxyProperty('redo_log_enabled')
