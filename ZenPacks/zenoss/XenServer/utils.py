######################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is
# installed.
#
######################################################################

from zope.event import notify

from Products.AdvancedQuery import Eq, Or

from Products.ZenModel.Device import Device
from Products.ZenModel.DeviceComponent import DeviceComponent
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.ZenModel.ZenossSecurity import ZEN_CHANGE_DEVICE
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
        else:
            relationship.removeRelation(obj)

        # Index remote object. It might have a custom path reporter.
        notify(IndexingEvent(obj, 'path', False))

        # For componentSearch. Would be nice if we could target
        # idxs=['getAllPaths'], but there's a chance that it won't exist
        # yet.
        obj.index_object()


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

    return


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

    uuid = None

    # Explicit inheritence.
    _properties = ManagedEntity._properties + (
        {'id': 'uuid', 'type': 'string', 'mode': 'w'},
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


class IBaseComponentInfo(IComponentInfo):
    '''
    Abstract base API Info interface for components.
    '''


class BaseComponentInfo(ComponentInfo):
    '''
    Abstract base API Info adapter factory for components.
    '''


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
