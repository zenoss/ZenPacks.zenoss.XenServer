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


class PBD(PooledComponent):
    '''
    Model class for PBD (physical block device.)
    '''

    meta_type = portal_type = 'XenServerPBD'

    current_attached = None
    dc_device = None
    dc_legacy_mode = None
    dc_location = None

    _properties = PooledComponent._properties + (
        {'id': 'current_attached', 'type': 'bool', 'mode': 'w'},
        {'id': 'dc_device', 'type': 'string', 'mode': 'w'},
        {'id': 'dc_legacy_mode', 'type': 'bool', 'mode': 'w'},
        {'id': 'dc_location', 'type': 'string', 'mode': 'w'},
        )

    _relations = PooledComponent._relations + (
        ('host', ToOne(ToManyCont, MODULE_NAME['Host'], 'pbds')),
        ('sr', ToOne(ToMany, MODULE_NAME['SR'], 'pbds')),
        )

    def getSR(self):
        '''
        Return SR id or None.

        Used by modeling.
        '''
        sr = self.sr()
        if sr:
            return sr.id

    def setSR(self, sr_id):
        '''
        Set SR by id.

        Used by modeling.
        '''
        updateToOne(
            relationship=self.sr,
            root=self.device(),
            type_=CLASS_NAME['SR'],
            id_=sr_id)


class IPBDInfo(IPooledComponentInfo):
    '''
    API Info interface for PBD.
    '''

    host = schema.Entity(title=_t(u'Host'))
    sr = schema.Entity(title=_t(u'Storage Repository'))

    current_attached = schema.Bool(title=_t(u'current_attacheds'))
    dc_device = schema.TextLine(title=_t(u'dc_devices'))
    dc_legacy_mode = schema.Bool(title=_t(u'dc_legacy_modes'))
    dc_location = schema.TextLine(title=_t(u'dc_locations'))


class PBDInfo(PooledComponentInfo):
    '''
    API Info adapter factory for PBD.
    '''

    implements(IPBDInfo)
    adapts(PBD)

    host = RelationshipInfoProperty('host')
    sr = RelationshipInfoProperty('sr')

    current_attached = ProxyProperty('current_attached')
    dc_device = ProxyProperty('dc_device')
    dc_legacy_mode = ProxyProperty('dc_legacy_mode')
    dc_location = ProxyProperty('dc_location')


class PBDPathReporter(DefaultPathReporter):
    '''
    Path reporter for PBD.
    '''

    def getPaths(self):
        paths = super(PBDPathReporter, self).getPaths()

        sr = self.context.sr()
        if sr:
            paths.extend(relPath(sr, 'endpoint'))

        return paths
