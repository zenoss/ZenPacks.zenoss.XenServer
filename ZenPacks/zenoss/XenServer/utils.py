######################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is
# installed.
#
######################################################################

import logging
LOG = logging.getLogger('zen.XenServer')

from zope.event import notify

from Products.AdvancedQuery import Eq, Or

from Products.ZenModel.Device import Device
from Products.ZenModel.DeviceComponent import DeviceComponent
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.ZenModel.ZenossSecurity import ZEN_CHANGE_DEVICE
from Products.ZenRelations.ToManyContRelationship import ToManyContRelationship
from Products.ZenUtils.Utils import prepId
from Products import Zuul
from Products.Zuul.catalog.events import IndexingEvent
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.component import ComponentInfo
from Products.Zuul.interfaces import ICatalogTool
from Products.Zuul.interfaces.component import IComponentInfo
from Products.Zuul.utils import ZuulMessageFactory as _t


def add_local_lib_path():
    '''
    Helper to add the ZenPack's lib directory to sys.path.
    '''
    import os
    import site

    site.addsitedir(os.path.join(os.path.dirname(__file__), 'lib'))


def updateToMany(relationship, root, type_, ids):
    '''
    Update ToMany relationship given search root, type and ids.

    This is a general-purpose function for efficiently building
    non-containing ToMany relationships.
    '''
    root = root.primaryAq()

    new_ids = set(map(prepId, ids))
    current_ids = set(o.id for o in relationship.objectValuesGen())
    changed_ids = new_ids.symmetric_difference(current_ids)

    query = Or(*(Eq('id', x) for x in changed_ids))

    obj_map = {}
    for result in ICatalogTool(root).search(types=[type_], query=query):
        obj_map[result.id] = result.getObject()

    for id_ in new_ids.symmetric_difference(current_ids):
        obj = obj_map.get(id_)
        if not obj:
            continue

        if id_ in new_ids:
            relationship.addRelation(obj)

            # Index remote object. It might have a custom path reporter.
            notify(IndexingEvent(obj, 'path', False))
        else:
            relationship.removeRelation(obj)

            # If the object was not deleted altogether..
            if not isinstance(relationship, ToManyContRelationship):
                # Index remote object. It might have a custom path reporter.
                notify(IndexingEvent(obj, 'path', False))

        # For componentSearch. Would be nice if we could target
        # Index remote object. It might have a custom path reporter.
        notify(IndexingEvent(obj, 'path', False))

        # For componentSearch. Would be nice if we could target
        # idxs=['getAllPaths'], but there's a chance that it won't exist
        # yet.
        obj.index_object()


def addToMany(relationship, root, type_, id_):
    '''
    Update ToMany relationship given search root, type and id.

    Adds a new ID to this relationship, without disturbing existing
    objects.
    '''
    root = root.primaryAq()
    query = Eq('id', id_)

    for result in ICatalogTool(root).search(types=[type_], query=query):
        obj = result.getObject()
        relationship.addRelation(obj)

        # Index remote object. It might have a custom path reporter.
        notify(IndexingEvent(obj, 'path', False))

        # For componentSearch. Would be nice if we could target
        # idxs=['getAllPaths'], but there's a chance that it won't exist
        # yet.
        obj.index_object()
        break


def removeToMany(relationship, root, type_, id_):
    '''
    Update ToMany relationship given search root, type and id.

    Removes a single ID from this relationship, without disturbing
    existing objects.
    '''
    root = root.primaryAq()
    query = Eq('id', id_)

    for result in ICatalogTool(root).search(types=[type_], query=query):
        obj = result.getObject()
        relationship.removeRelation()

        # Index remote object. It might have a custom path reporter.
        notify(IndexingEvent(obj, 'path', False))

        # For componentSearch. Would be nice if we could target
        # idxs=['getAllPaths'], but there's a chance that it won't exist
        # yet.
        obj.index_object()
        break


def updateToOne(relationship, root, type_, id_):
    '''
    Update ToOne relationship given search root, type and ids.

    This is a general-purpose function for efficiently building
    non-containing ToOne relationships.
    '''
    old_obj = relationship()

    # Return with no action if the relationship is already correct.
    if (old_obj and old_obj.id == id_) or (not old_obj and not id_):
        return

    # Remove current object from relationship.
    if old_obj:
        relationship.removeRelation()

        # Index old object. It might have a custom path reporter.
        notify(IndexingEvent(old_obj.primaryAq(), 'path', False))

    # No need to find new object if id_ is empty.
    if not id_:
        return

    # Find and add new object to relationship.
    root = root.primaryAq()
    query = Eq('id', id_)

    for result in ICatalogTool(root).search(types=[type_], query=query):
        new_obj = result.getObject()
        relationship.addRelation(new_obj)

        # Index remote object. It might have a custom path reporter.
        notify(IndexingEvent(new_obj.primaryAq(), 'path', False))

        # For componentSearch. Would be nice if we could target
        # idxs=['getAllPaths'], but there's a chance that it won't exist
        # yet.
        new_obj.index_object()
        break


def RelationshipInfoProperty(relationship_name):
    '''
    Return a read-only property with the Infos for object(s) in the
    relationship.

    A list of Info objects is returned for ToMany relationships, and a
    single Info object is returned for ToOne relationships.
    '''
    def getter(self):
        return Zuul.info(getattr(self._object, relationship_name)())

    return property(getter)


def RelationshipLengthProperty(relationship_name):
    '''
    Return a read-only property with a value equal to the number of
    objects in the relationship named relationship_name.
    '''
    def getter(self):
        relationship = getattr(self._object, relationship_name)
        try:
            return relationship.countObjects()
        except Exception:
            return len(relationship())

    return property(getter)


class BaseComponent(DeviceComponent, ManagedEntity):
    '''
    Abstract base class for components.
    '''

    xenapi_ref = None
    xenapi_uuid = None

    # Explicit inheritence.
    _properties = ManagedEntity._properties + (
        {'id': 'xenapi_ref', 'type': 'string', 'mode': 'w'},
        {'id': 'xenapi_uuid', 'type': 'string', 'mode': 'w'},
        )

    _relations = ManagedEntity._relations

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

    def index_object(self, idxs=None):
        '''
        Overrides to also catalog in XenServerCatalog.
        '''
        super(BaseComponent, self).index_object(idxs=idxs)
        getXenServerCatalog(self.dmd).catalog_object(self, self.getPrimaryId())

    def unindex_object(self):
        '''
        Overrides to also uncatalog in XenServerCatalog.
        '''
        super(BaseComponent, self).unindex_object()
        getXenServerCatalog(self.dmd).uncatalog_object(self.getPrimaryId())

    def getRRDTemplateName(self):
        '''
        Return name of monitoring template to bind to this component.
        '''
        return self.__class__.__name__

    def xenrrd_prefix(self):
        '''
        Return prefix under which XenServer stores RRD data about this
        component.

        Prefix must be a three element tuple that looks like one of the
        following examples::

            ('host', 'host-uuid', '')
            ('host', 'host-uuid', 'sr_sr-uuid_')

        No generic implementation exists. Must be overridden in
        subclasses to which XenServer RRD datasources will be bound.
        '''
        return None

    @classmethod
    def objectmap(cls, ref, properties):
        '''
        Return an ObjectMap given XenAPI ref and properties.

        No generic implementation exists. Must be overridden in
        subclasses that are modeled.
        '''
        return None

    @classmethod
    def objectmap_metrics(cls, ref, properties):
        '''
        Return an ObjectMap given XenAPI ref and metrics properties.

        No generic implementation exists. Must be overridden in
        subclasses that have properties modeled from their corresponding
        _metrics class.
        '''
        return None


class IBaseComponentInfo(IComponentInfo):
    '''
    Abstract base API Info interface for components.
    '''

    endpoint = schema.Entity(title=_t('Endpoint'))
    xenapi_ref = schema.TextLine(title=_t(u'XenAPI Reference'))
    xenapi_uuid = schema.TextLine(title=_t(u'XenAPI UUID'))


class BaseComponentInfo(ComponentInfo):
    '''
    Abstract base API Info adapter factory for components.
    '''

    endpoint = RelationshipInfoProperty('device')
    xenapi_ref = ProxyProperty('xenapi_ref')
    xenapi_uuid = ProxyProperty('xenapi_uuid')


class PooledComponent(BaseComponent):
    '''
    Abstract base class for all pooled components.
    '''

    def pool(self):
        '''
        Return the pool containing this component.

        For a non-pooled resource return None.
        '''
        for pool in self.device().pools.objectValuesGen():
            return pool


class IPooledComponentInfo(IBaseComponentInfo):
    '''
    Abstract base API Info interface for pooled components.
    '''

    pool = schema.Entity(title=_t(u'Pool'))


class PooledComponentInfo(BaseComponentInfo):
    '''
    Abstract base API Info adapter factory for pooled components.
    '''

    pool = RelationshipInfoProperty('pool')


def getXenServerCatalog(dmd):
    '''
    Return the XenServerCatalog.

    Creates the catalog if it doesn't already exist.
    '''
    try:
        return dmd.Devices.XenServer.XenServerCatalog
    except AttributeError:
        return createXenServerCatalog(dmd)


def createXenServerCatalog(dmd):
    '''
    Create /zport/dmd/Devices/XenServer/XenServerCatalog and return it.

    This allows for fast lookup of XenServer components by their XenAPI
    UUID.
    '''
    from Products.ZCatalog.Catalog import CatalogError
    from Products.ZCatalog.ZCatalog import manage_addZCatalog

    from Products.ZenUtils.Search import makeCaseSensitiveFieldIndex
    from Products.Zuul.interfaces import ICatalogTool

    catalog_name = 'XenServerCatalog'
    device_class = dmd.Devices.createOrganizer('/XenServer')

    if not hasattr(device_class, catalog_name):
        LOG.info('Creating XenServer catalog')
        manage_addZCatalog(device_class, catalog_name, catalog_name)

    zcatalog = device_class._getOb(catalog_name)
    catalog = zcatalog._catalog

    try:
        catalog.addIndex(
            'xenapi_uuid',
            makeCaseSensitiveFieldIndex('xenapi_uuid'))

    except CatalogError:
        # Index already exists.
        pass

    else:
        results = ICatalogTool(dmd.primaryAq()).search(
            'ZenPacks.zenoss.XenServer.utils.BaseComponent')

        if results.total:
            LOG.info('Reindexing all XenServer components')
            for brain in results:
                brain.getObject().index_object()

    return catalog


def findComponentByUUID(dmd, xenapi_uuid):
    '''
    Return the first XenServer component matching XenAPI uuid.
    '''
    if not xenapi_uuid:
        return

    for brain in getXenServerCatalog(dmd)(xenapi_uuid=xenapi_uuid):
        return brain.getObject()


def findIpInterfacesByMAC(dmd, macaddresses, interfaceType=None):
    '''
    Yield IpInterface objects that match the parameters.
    '''
    if not macaddresses:
        return

    layer2_catalog = dmd.ZenLinkManager._getCatalog(layer=2)
    if layer2_catalog is not None:
        for result in layer2_catalog(macaddress=macaddresses):
            iface = result.getObject()
            if not interfaceType or isinstance(iface, interfaceType):
                yield iface


def id_from_ref(ref):
    '''
    Return a component id given a XenAPI OpaqueRef.
    '''
    if not ref or ref == 'OpaqueRef:NULL':
        return None

    return prepId(ref.split(':', 1)[1])


def ids_from_refs(refs):
    '''
    Return list of component ids given a list of XenAPI OpaqueRefs.

    Null references won't be included in the returned list. So it's
    possible that the returned list will be shorter than the passed
    list.
    '''
    ids = []

    for ref in refs:
        id_ = id_from_ref(ref)
        if id_:
            ids.append(id_)

    return ids


def int_or_none(value):
    '''
    Return value converted to int or None if conversion fails.
    '''
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def float_or_none(value):
    '''
    Return value converted to float or None if conversion fails.
    '''
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def to_boolean(value, true_value='true'):
    '''
    Return value converted to boolean.
    '''
    if value == true_value:
        return True
    else:
        return False
