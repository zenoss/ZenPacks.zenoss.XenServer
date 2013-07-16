
######################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is
# installed.
#
######################################################################

from zope.interface import implements
from Products.ZenModel.ZenossSecurity import ZEN_CHANGE_DEVICE
from Products.Zuul.decorators import info
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.utils import ZuulMessageFactory as _t
from Products.ZenModel.DeviceComponent import DeviceComponent
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.Zuul.catalog.paths import DefaultPathReporter, relPath
from Products.Zuul.infos.component import ComponentInfo
from Products.Zuul.interfaces.component import IComponentInfo
from Products.ZenRelations.RelSchema import ToMany,ToManyCont,ToOne
from Products.ZenRelations.RelSchema import ToManyCont,ToOne

class Pool(DeviceComponent, ManagedEntity):
    meta_type = portal_type = 'XenServerPool'

    Klasses = [DeviceComponent, ManagedEntity]

    vswitch_controller = None
    ha_enabled = None
    ha_plan_exists_for = None
    name_label = None
    ha_allow_overcommit = None
    ha_host_failures_to_tolerate = None
    name_description = None
    ha_overcommitted = None
    redo_log_enabled = None
    uuid = None

    _properties = ()
    for Klass in Klasses:
        _properties = _properties + getattr(Klass,'_properties', ())

    _properties = _properties + (
        {'id': 'vswitch_controller', 'type': 'string', 'mode': 'w'},
        {'id': 'ha_enabled', 'type': 'bool', 'mode': 'w'},
        {'id': 'ha_plan_exists_for', 'type': 'int', 'mode': 'w'},
        {'id': 'name_label', 'type': 'string', 'mode': 'w'},
        {'id': 'ha_allow_overcommit', 'type': 'bool', 'mode': 'w'},
        {'id': 'ha_host_failures_to_tolerate', 'type': 'int', 'mode': 'w'},
        {'id': 'name_description', 'type': 'string', 'mode': 'w'},
        {'id': 'ha_overcommitted', 'type': 'bool', 'mode': 'w'},
        {'id': 'redo_log_enabled', 'type': 'bool', 'mode': 'w'},
        {'id': 'uuid', 'type': 'string', 'mode': 'w'},
        )

    _relations = ()
    for Klass in Klasses:
        _relations = _relations + getattr(Klass, '_relations', ())

    _relations = _relations + (
        ('endpoint', ToOne(ToManyCont, 'ZenPacks.zenoss.XenServer.Endpoint', 'pools',)),
        )

    factory_type_information = ({
        'actions': ({
            'id': 'perfConf',
            'name': 'Template',
            'action': 'objTemplates',
            'permissions': (ZEN_CHANGE_DEVICE,),
            },),
        },)

    def device(self):
        '''
        Return device under which this component/device is contained.
        '''
        obj = self

        for i in range(200):
            if isinstance(obj, Device):
                return obj

            try:
                obj = obj.getPrimaryParent()
            except AttributeError as exc:
                raise AttributeError(
                    'Unable to determine parent at %s (%s) '
                    'while getting device for %s' % (
                        obj, exc, self))

class IPoolInfo(IComponentInfo):

    vswitch_controller = schema.TextLine(title=_t(u'vswitch_controllers'))
    ha_enabled = schema.Bool(title=_t(u'ha_enableds'))
    ha_plan_exists_for = schema.Int(title=_t(u'ha_plan_exists_fors'))
    name_label = schema.TextLine(title=_t(u'name_labels'))
    ha_allow_overcommit = schema.Bool(title=_t(u'ha_allow_overcommits'))
    ha_host_failures_to_tolerate = schema.Int(title=_t(u'ha_host_failures_to_tolerates'))
    name_description = schema.TextLine(title=_t(u'name_descriptions'))
    ha_overcommitted = schema.Bool(title=_t(u'ha_overcommitteds'))
    redo_log_enabled = schema.Bool(title=_t(u'redo_log_enableds'))
    uuid = schema.TextLine(title=_t(u'uuids'))

class PoolInfo(ComponentInfo):
    implements(IPoolInfo)

    vswitch_controller = ProxyProperty('vswitch_controller')
    ha_enabled = ProxyProperty('ha_enabled')
    ha_plan_exists_for = ProxyProperty('ha_plan_exists_for')
    name_label = ProxyProperty('name_label')
    ha_allow_overcommit = ProxyProperty('ha_allow_overcommit')
    ha_host_failures_to_tolerate = ProxyProperty('ha_host_failures_to_tolerate')
    name_description = ProxyProperty('name_description')
    ha_overcommitted = ProxyProperty('ha_overcommitted')
    redo_log_enabled = ProxyProperty('redo_log_enabled')
    uuid = ProxyProperty('uuid')

