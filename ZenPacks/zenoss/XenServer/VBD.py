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
    PooledComponent, IPooledComponentInfo, PooledComponentInfo,
    RelationshipInfoProperty,
    updateToOne,
    )


class VBD(PooledComponent):
    '''
    Model class for VBD (virtual block device.)
    '''

    meta_type = portal_type = 'XenServerVBD'

    xapi_metrics_ref = None
    allowed_operations = None
    bootable = None
    currently_attached = None
    vbd_device = None
    empty = None
    mode = None
    storage_lock = None
    vbd_type = None
    unpluggable = None
    userdevice = None

    _properties = PooledComponent._properties + (
        {'id': 'xapi_metrics_ref', 'type': 'string', 'mode': 'w'},
        {'id': 'allowed_operations', 'type': 'lines', 'mode': 'w'},
        {'id': 'bootable', 'type': 'boolean', 'mode': 'w'},
        {'id': 'currently_attached', 'type': 'boolean', 'mode': 'w'},
        {'id': 'vbd_device', 'type': 'string', 'mode': 'w'},
        {'id': 'empty', 'type': 'boolean', 'mode': 'w'},
        {'id': 'mode', 'type': 'string', 'mode': 'w'},
        {'id': 'storage_lock', 'type': 'boolean', 'mode': 'w'},
        {'id': 'vbd_type', 'type': 'string', 'mode': 'w'},
        {'id': 'unpluggable', 'type': 'boolean', 'mode': 'w'},
        {'id': 'userdevice', 'type': 'string', 'mode': 'w'},
        )

    _relations = PooledComponent._relations + (
        ('vm', ToOne(ToManyCont, MODULE_NAME['VM'], 'vbds')),
        ('vdi', ToOne(ToMany, MODULE_NAME['VDI'], 'vbds')),
        )

    def getVDI(self):
        '''
        Return VDI id or None.

        Used by modeling.
        '''
        vdi = self.vdi()
        if vdi:
            return vdi.id

    def setVDI(self, vdi_id):
        '''
        Set VDI by id.

        Used by modeling.
        '''
        updateToOne(
            relationship=self.vdi,
            root=self.device(),
            type_=CLASS_NAME['VDI'],
            id_=vdi_id)

    def xenrrd_prefix(self):
        '''
        Return prefix under which XenServer stores RRD data about this
        component.
        '''
        vm_uuid = self.vm().xapi_uuid
        if vm_uuid and self.vbd_device:
            return ('vm', vm_uuid, '_'.join(('vbd', self.vbd_device)))


class IVBDInfo(IPooledComponentInfo):
    '''
    API Info interface for VBD.
    '''

    vm = schema.Entity(title=_t(u'VM'))
    vdi = schema.Entity(title=_t(u'VDI'))

    allowed_operations = schema.TextLine(title=_t(u'Allowed Operations'))
    bootable = schema.TextLine(title=_t(u'Bootable'))
    currently_attached = schema.TextLine(title=_t(u'Currently Attached'))
    vbd_device = schema.TextLine(title=_t(u'Device Name'))
    empty = schema.TextLine(title=_t(u'Empty'))
    mode = schema.TextLine(title=_t(u'Mode'))
    storage_lock = schema.TextLine(title=_t(u'Storage Lock'))
    vbd_type = schema.TextLine(title=_t(u'Type'))
    unpluggable = schema.TextLine(title=_t(u'Unpluggable'))
    userdevice = schema.TextLine(title=_t(u'User Device'))


class VBDInfo(PooledComponentInfo):
    '''
    API Info adapter factory for VBD.
    '''

    implements(IVBDInfo)
    adapts(VBD)

    vm = RelationshipInfoProperty('vm')
    vdi = RelationshipInfoProperty('vdi')

    xapi_metrics_ref = ProxyProperty('xapi_metrics_ref')
    allowed_operations = ProxyProperty('allowed_operations')
    bootable = ProxyProperty('bootable')
    currently_attached = ProxyProperty('currently_attached')
    vbd_device = ProxyProperty('vbd_device')
    empty = ProxyProperty('empty')
    mode = ProxyProperty('mode')
    storage_lock = ProxyProperty('storage_lock')
    vbd_type = ProxyProperty('vbd_type')
    unpluggable = ProxyProperty('unpluggable')
    userdevice = ProxyProperty('userdevice')


class VBDPathReporter(DefaultPathReporter):
    '''
    Path reporter for VBD.
    '''

    def getPaths(self):
        paths = super(VBDPathReporter, self).getPaths()

        vdi = self.context.vdi()
        if vdi:
            paths.extend(relPath(vdi, 'sr'))

        vapp = self.context.vm().vmappliance()
        if vapp:
            paths.extend(relPath(vapp, 'endpoint'))

        return paths
