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
from Products.Zuul.catalog.paths import DefaultPathReporter, relPath
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.utils import ZuulMessageFactory as _t

from ZenPacks.zenoss.XenServer import CLASS_NAME, MODULE_NAME
from ZenPacks.zenoss.XenServer.utils import (
    BaseComponent, IBaseComponentInfo, BaseComponentInfo,
    RelationshipLengthProperty,
    updateToOne,
    )


class VM(BaseComponent):
    '''
    Model class for VM.
    '''

    meta_type = portal_type = 'XenServerVM'

    memory_static_min = None
    name_label = None
    VCPUs_max = None
    memory_static_max = None
    VCPUs_at_startup = None
    memory_dynamic_max = None
    power_state = None
    name_description = None
    memory_dynamic_min = None
    memory_overhead = None

    _properties = BaseComponent._properties + (
        {'id': 'memory_static_min', 'type': 'string', 'mode': 'w'},
        {'id': 'name_label', 'type': 'string', 'mode': 'w'},
        {'id': 'VCPUs_max', 'type': 'string', 'mode': 'w'},
        {'id': 'memory_static_max', 'type': 'string', 'mode': 'w'},
        {'id': 'VCPUs_at_startup', 'type': 'string', 'mode': 'w'},
        {'id': 'memory_dynamic_max', 'type': 'string', 'mode': 'w'},
        {'id': 'power_state', 'type': 'string', 'mode': 'w'},
        {'id': 'name_description', 'type': 'string', 'mode': 'w'},
        {'id': 'memory_dynamic_min', 'type': 'string', 'mode': 'w'},
        {'id': 'memory_overhead', 'type': 'string', 'mode': 'w'},
        )

    _relations = BaseComponent._relations + (
        ('endpoint', ToOne(ToManyCont, MODULE_NAME['Endpoint'], 'vms')),
        ('host', ToOne(ToMany, MODULE_NAME['Host'], 'vms')),
        ('vmappliance', ToOne(ToMany, MODULE_NAME['VMAppliance'], 'vms')),
        ('vbds', ToManyCont(ToOne, MODULE_NAME['VBD'], 'vm')),
        ('vifs', ToManyCont(ToOne, MODULE_NAME['VIF'], 'vm')),
        )

    def getHostId(self):
        '''
        Return host id or None.

        Used by modeling.
        '''
        obj = self.host()
        if obj:
            return obj.id

    def setHostId(self, id_):
        '''
        Set host by id.

        Used by modeling.
        '''
        updateToOne(
            relationship=self.host,
            root=self.device(),
            type_=CLASS_NAME['Host'],
            id_=id_)


class IVMInfo(IBaseComponentInfo):
    '''
    API Info interface for VM.
    '''

    name_label = schema.TextLine(title=_t(u'Name'))
    name_description = schema.TextLine(title=_t(u'Description'))
    memory_static_min = schema.TextLine(title=_t(u'memory_static_mins'))
    VCPUs_max = schema.TextLine(title=_t(u'VCPUs_maxes'))
    memory_static_max = schema.TextLine(title=_t(u'memory_static_maxes'))
    VCPUs_at_startup = schema.TextLine(title=_t(u'VCPUs_at_startups'))
    memory_dynamic_max = schema.TextLine(title=_t(u'memory_dynamic_maxes'))
    power_state = schema.TextLine(title=_t(u'power_states'))
    memory_dynamic_min = schema.TextLine(title=_t(u'memory_dynamic_mins'))
    memory_overhead = schema.TextLine(title=_t(u'memory_overheads'))

    vbd_count = schema.Int(title=_t(u'Number of VBDS'))
    vif_count = schema.Int(title=_t(u'Number of VIFS'))


class VMInfo(BaseComponentInfo):
    '''
    API Info adapter factory for VM.
    '''

    implements(IVMInfo)
    adapts(VM)

    memory_static_min = ProxyProperty('memory_static_min')
    name_label = ProxyProperty('name_label')
    VCPUs_max = ProxyProperty('VCPUs_max')
    memory_static_max = ProxyProperty('memory_static_max')
    VCPUs_at_startup = ProxyProperty('VCPUs_at_startup')
    memory_dynamic_max = ProxyProperty('memory_dynamic_max')
    power_state = ProxyProperty('power_state')
    name_description = ProxyProperty('name_description')
    memory_dynamic_min = ProxyProperty('memory_dynamic_min')
    memory_overhead = ProxyProperty('memory_overhead')

    vbd_count = RelationshipLengthProperty('vbds')
    vif_count = RelationshipLengthProperty('vifs')


class VMPathReporter(DefaultPathReporter):
    '''
    Path reporter for VM.
    '''

    def getPaths(self):
        paths = super(VMPathReporter, self).getPaths()

        host = self.context.host()
        if host:
            paths.extend(relPath(host, 'endpoint'))

        vapp = self.context.vmappliance()
        if vapp:
            paths.extend(relPath(vapp, 'endpoint'))

        return paths
