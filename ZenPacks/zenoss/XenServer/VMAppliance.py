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


class VMAppliance(BaseComponent):
    '''
    Model class for VMAppliance. Also known as vApp.
    '''

    meta_type = portal_type = 'XenServerVMAppliance'

    name_label = None
    name_description = None

    _properties = BaseComponent._properties + (
        {'id': 'name_label', 'type': 'string', 'mode': 'w'},
        {'id': 'name_description', 'type': 'string', 'mode': 'w'},
        )

    _relations = BaseComponent._relations + (
        ('endpoint', ToOne(ToManyCont, MODULE_NAME['Endpoint'], 'vmappliances',)),
        ('vms', ToMany(ToOne, MODULE_NAME['VM'], 'vmappliance')),
        )

    def getVMs(self):
        '''
        Return a sorted list of related VM ids.
        Aggregate.

        Used by modeling.
        '''
        return sorted([vm.id for vm in self.vms.objectValuesGen()])

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


class IVMApplianceInfo(IBaseComponentInfo):
    '''
    API Info interface for VMAppliance.
    '''

    name_label = schema.TextLine(title=_t(u'Name'))
    name_description = schema.TextLine(title=_t(u'Description'))

    vm_count = schema.Int(title=_t(u'Number of VMs'))


class VMApplianceInfo(BaseComponentInfo):
    '''
    API Info adapter factory for VMAppliance.
    '''

    implements(IVMApplianceInfo)
    adapts(VMAppliance)

    name_label = ProxyProperty('name_label')
    name_description = ProxyProperty('name_description')

    vm_count = RelationshipLengthProperty('vms')
