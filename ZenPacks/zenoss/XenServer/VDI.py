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

from Products.DataCollector.plugins.DataMaps import ObjectMap
from Products.ZenRelations.RelSchema import ToMany, ToManyCont, ToOne
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.utils import ZuulMessageFactory as _t

from ZenPacks.zenoss.XenServer import CLASS_NAME, MODULE_NAME
from ZenPacks.zenoss.XenServer.utils import (
    PooledComponent, IPooledComponentInfo, PooledComponentInfo,
    RelationshipInfoProperty, RelationshipLengthProperty,
    updateToMany,
    id_from_ref, ids_from_refs,
    )


class VDI(PooledComponent):
    '''
    Model class for VDI (virtual disk image.)
    '''
    meta_type = portal_type = 'XenServerVDI'

    allow_caching = None
    allowed_operations = None
    is_a_snapshot = None
    location = None
    managed = None
    missing = None
    name_description = None
    name_label = None
    on_boot = None
    read_only = None
    sharable = None
    storage_lock = None
    vdi_type = None
    virtual_size = None

    _properties = PooledComponent._properties + (
        {'id': 'allow_caching', 'type': 'boolean', 'mode': 'w'},
        {'id': 'allowed_operations', 'type': 'lines', 'mode': 'w'},
        {'id': 'is_a_snapshot', 'type': 'boolean', 'mode': 'w'},
        {'id': 'location', 'type': 'string', 'mode': 'w'},
        {'id': 'managed', 'type': 'boolean', 'mode': 'w'},
        {'id': 'missing', 'type': 'boolean', 'mode': 'w'},
        {'id': 'name_description', 'type': 'string', 'mode': 'w'},
        {'id': 'name_label', 'type': 'string', 'mode': 'w'},
        {'id': 'on_boot', 'type': 'string', 'mode': 'w'},
        {'id': 'read_only', 'type': 'boolean', 'mode': 'w'},
        {'id': 'sharable', 'type': 'boolean', 'mode': 'w'},
        {'id': 'storage_lock', 'type': 'boolean', 'mode': 'w'},
        {'id': 'vdi_type', 'type': 'string', 'mode': 'w'},
        {'id': 'virtual_size', 'type': 'int', 'mode': 'w'},
        )

    _relations = PooledComponent._relations + (
        ('sr', ToOne(ToManyCont, MODULE_NAME['SR'], 'vdis')),
        ('vbds', ToMany(ToOne, MODULE_NAME['VBD'], 'vdi')),
        )

    @classmethod
    def objectmap(cls, ref, properties):
        '''
        Return an ObjectMap given XenAPI VDI ref and properties.
        '''
        title = properties.get('name_label') or \
            properties.get('location') or \
            properties['uuid']

        return ObjectMap(data={
            'compname': 'srs/{}'.format(id_from_ref(properties.get('SR'))),
            'relname': 'vdis',
            'id': id_from_ref(ref),
            'title': title,
            'xenapi_ref': ref,
            'xenapi_uuid': properties.get('uuid'),
            'allow_caching': properties.get('allow_caching'),
            'allowed_operations': properties.get('allowed_operations'),
            'is_a_snapshot': properties.get('is_a_snapshot'),
            'location': properties.get('location'),
            'managed': properties.get('managed'),
            'missing': properties.get('missing'),
            'name_description': properties.get('name_description'),
            'name_label': properties.get('name_label'),
            'on_boot': properties.get('on_boot'),
            'read_only': properties.get('read_only'),
            'sharable': properties.get('sharable'),
            'storage_lock': properties.get('storage_lock'),
            'vdi_type': properties.get('type'),
            'virtual_size': properties.get('virtual_size'),
            'setVBDs': ids_from_refs(properties.get('VBDs', [])),
            }, modname=cls.__module__)

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

    def xenrrd_prefix(self):
        '''
        Return prefix under which XenServer stores RRD data about this
        component.
        '''
        # This is a guess at future support. XenServer 6.2 doesn't have
        # any RRD data for VDIs.
        if self.xenapi_uuid:
            return ('vdi', self.xenapi_uuid, '')


class IVDIInfo(IPooledComponentInfo):
    '''
    API Info interface for VBD.
    '''

    sr = schema.Entity(title=_t(u'Storage Repository'))

    allow_caching = schema.Bool(title=_t(u'Allow Caching'))
    allowed_operations = schema.Text(title=_t(u'Allowed Operations'))
    is_a_snapshot = schema.Bool(title=_t(u'Is a Snapshot'))
    location = schema.TextLine(title=_t(u'Location'))
    managed = schema.Bool(title=_t(u'Managed'))
    missing = schema.Bool(title=_t(u'Missing'))
    name_description = schema.TextLine(title=_t(u'Description'))
    name_label = schema.TextLine(title=_t(u'Label'))
    on_boot = schema.TextLine(title=_t(u'On Boot'))
    read_only = schema.Bool(title=_t(u'Read Only'))
    sharable = schema.Bool(title=_t(u'Sharable'))
    storage_lock = schema.Bool(title=_t(u'Storage Lock'))
    vdi_type = schema.TextLine(title=_t(u'Type'))
    virtual_size = schema.Int(title=_t(u'Virtual Size'))

    vbd_count = schema.Int(title=_t(u'Number of Virtual Block Devices'))


class VDIInfo(PooledComponentInfo):
    '''
    API Info adapter factory for VBD.
    '''

    implements(IVDIInfo)
    adapts(VDI)

    sr = RelationshipInfoProperty('sr')

    allow_caching = ProxyProperty('allow_caching')
    allowed_operations = ProxyProperty('allowed_operations')
    is_a_snapshot = ProxyProperty('is_a_snapshot')
    location = ProxyProperty('location')
    managed = ProxyProperty('managed')
    missing = ProxyProperty('missing')
    name_description = ProxyProperty('name_description')
    name_label = ProxyProperty('name_label')
    on_boot = ProxyProperty('on_boot')
    read_only = ProxyProperty('read_only')
    sharable = ProxyProperty('sharable')
    storage_lock = ProxyProperty('storage_lock')
    vdi_type = ProxyProperty('vdi_type')
    virtual_size = ProxyProperty('virtual_size')

    vbd_count = RelationshipLengthProperty('vbds')
