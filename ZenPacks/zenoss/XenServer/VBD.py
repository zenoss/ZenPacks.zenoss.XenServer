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
    updateToOne,
    )


class VBD(BaseComponent):
    '''
    Model class for VBD (virtual block device.)
    '''

    meta_type = portal_type = 'XenServerVBD'

    bootable = None
    status_code = None
    status_detail = None
    current_attached = None
    Type = None
    empty = None

    _properties = BaseComponent._properties + (
        {'id': 'bootable', 'type': 'string', 'mode': 'w'},
        {'id': 'status_code', 'type': 'string', 'mode': 'w'},
        {'id': 'status_detail', 'type': 'string', 'mode': 'w'},
        {'id': 'current_attached', 'type': 'string', 'mode': 'w'},
        {'id': 'Type', 'type': 'string', 'mode': 'w'},
        {'id': 'empty', 'type': 'string', 'mode': 'w'},
        )

    _relations = BaseComponent._relations + (
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


class IVBDInfo(IBaseComponentInfo):
    '''
    API Info interface for VBD.
    '''

    bootable = schema.TextLine(title=_t(u'bootables'))
    status_code = schema.TextLine(title=_t(u'status_codes'))
    status_detail = schema.TextLine(title=_t(u'status_details'))
    current_attached = schema.TextLine(title=_t(u'current_attacheds'))
    Type = schema.TextLine(title=_t(u'Types'))
    empty = schema.TextLine(title=_t(u'empties'))


class VBDInfo(BaseComponentInfo):
    '''
    API Info adapter factory for VBD.
    '''

    implements(IVBDInfo)
    adapts(VBD)

    bootable = ProxyProperty('bootable')
    status_code = ProxyProperty('status_code')
    status_detail = ProxyProperty('status_detail')
    current_attached = ProxyProperty('current_attached')
    Type = ProxyProperty('Type')
    empty = ProxyProperty('empty')


class VBDPathReporter(DefaultPathReporter):
    '''
    Path reporter for VBD.
    '''

    def getPaths(self):
        paths = super(VBDPathReporter, self).getPaths()

        vdi = self.context.vdi()
        if vdi:
            paths.extend(relPath(vdi, 'endpoint'))

        return paths
