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
    )


class VDI(PooledComponent):
    '''
    Model class for VDI (virtual disk image.)
    '''
    meta_type = portal_type = 'XenServerVDI'

    name_label = None
    name_description = None
    read_only = None
    sharable = None
    missing = None
    physical_utilisation = None
    allow_caching = None
    on_boot = None
    virtual_size = None
    Type = None

    _properties = PooledComponent._properties + (
        {'id': 'name_label', 'type': 'string', 'mode': 'w'},
        {'id': 'name_description', 'type': 'string', 'mode': 'w'},
        {'id': 'read_only', 'type': 'string', 'mode': 'w'},
        {'id': 'sharable', 'type': 'string', 'mode': 'w'},
        {'id': 'missing', 'type': 'string', 'mode': 'w'},
        {'id': 'physical_utilisation', 'type': 'string', 'mode': 'w'},
        {'id': 'allow_caching', 'type': 'string', 'mode': 'w'},
        {'id': 'on_boot', 'type': 'string', 'mode': 'w'},
        {'id': 'virtual_size', 'type': 'string', 'mode': 'w'},
        {'id': 'Type', 'type': 'string', 'mode': 'w'},
        )

    _relations = PooledComponent._relations + (
        ('sr', ToOne(ToManyCont, MODULE_NAME['SR'], 'vdis')),
        ('vbds', ToMany(ToOne, MODULE_NAME['VBD'], 'vdi')),
        )

    def getVBDs(self):
        '''
        Return a sorted list of ids in the vbds relationship.

        Used by modeling.
        '''

        return sorted(vbd.id for vbd in self.vbds.objectValuesGen())

    def setVBDs(self, vbd_ids):
        '''
        Update vbds relationship given vbd_ids.

        Used by modeling.
        '''
        updateToMany(
            relationship=self.vbds,
            root=self.device(),
            type_=CLASS_NAME['VBD'],
            ids=vbd_ids)


class IVDIInfo(IPooledComponentInfo):
    '''
    API Info interface for VBD.
    '''

    name_label = schema.TextLine(title=_t(u'name_labels'))
    name_description = schema.TextLine(title=_t(u'name_descriptions'))
    read_only = schema.TextLine(title=_t(u'read_onlies'))
    sharable = schema.TextLine(title=_t(u'sharables'))
    missing = schema.TextLine(title=_t(u'missings'))
    physical_utilisation = schema.TextLine(title=_t(u'physical_utilisations'))
    allow_caching = schema.TextLine(title=_t(u'allow_cachings'))
    on_boot = schema.TextLine(title=_t(u'on_boots'))
    virtual_size = schema.TextLine(title=_t(u'virtual_sizes'))
    Type = schema.TextLine(title=_t(u'Types'))

    vbd_count = schema.Int(title=_t(u'Number of VBDS'))


class VDIInfo(PooledComponentInfo):
    '''
    API Info adapter factory for VBD.
    '''

    implements(IVDIInfo)
    adapts(VDI)

    name_label = ProxyProperty('name_label')
    name_description = ProxyProperty('name_description')
    read_only = ProxyProperty('read_only')
    sharable = ProxyProperty('sharable')
    missing = ProxyProperty('missing')
    physical_utilisation = ProxyProperty('physical_utilisation')
    allow_caching = ProxyProperty('allow_caching')
    on_boot = ProxyProperty('on_boot')
    virtual_size = ProxyProperty('virtual_size')
    Type = ProxyProperty('Type')

    vbd_count = RelationshipLengthProperty('vbds')
