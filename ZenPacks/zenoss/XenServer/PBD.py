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
from Products.ZenUtils.Utils import prepId
from Products.Zuul.catalog.paths import DefaultPathReporter, relPath
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.utils import ZuulMessageFactory as _t

from ZenPacks.zenoss.XenServer import CLASS_NAME, MODULE_NAME
from ZenPacks.zenoss.XenServer.utils import (
    PooledComponent, IPooledComponentInfo, PooledComponentInfo,
    RelationshipInfoProperty,
    updateToOne,
    id_from_ref, to_boolean,
    )


class PBD(PooledComponent):
    '''
    Model class for PBD (physical block device.)
    '''

    class_label = 'Physical Block Device'
    class_plural_label = 'Physical Block Devices'
    order = 14

    meta_type = portal_type = 'XenServerPBD'

    currently_attached = None
    dc_device = None
    dc_legacy_mode = None
    dc_location = None

    _properties = PooledComponent._properties + (
        {'id': 'currently_attached', 'label': 'Currently Attached', 'type': 'boolean', 'mode': 'w'},
        {'id': 'dc_device', 'label': 'Device Name', 'type': 'string', 'mode': 'w'},
        {'id': 'dc_legacy_mode', 'label': 'Legacy Mode', 'type': 'boolean', 'mode': 'w'},
        {'id': 'dc_location', 'label': 'Location', 'type': 'string', 'mode': 'w'},
        )

    _relations = PooledComponent._relations + (
        ('host', ToOne(ToManyCont, MODULE_NAME['Host'], 'pbds')),
        ('sr', ToOne(ToMany, MODULE_NAME['SR'], 'pbds')),
        )

    @classmethod
    def objectmap(cls, ref, properties):
        '''
        Return an ObjectMap given XenAPI PBD ref and properties.
        '''
        if 'uuid' not in properties:
            return {
                'compname': 'hosts/{}'.format(id_from_ref(properties['parent'])),
                'relname': 'pbds',
                'id': id_from_ref(ref),
                }

        device_config = properties.get('device_config', {})

        title = device_config.get('location') or \
            device_config.get('device') or \
            properties['uuid']

        return {
            'compname': 'hosts/{}'.format(id_from_ref(properties.get('host'))),
            'relname': 'pbds',
            'id': id_from_ref(ref),
            'title': title,
            'xenapi_ref': ref,
            'xenapi_uuid': properties.get('uuid'),
            'currently_attached': properties.get('currently_attached'),
            'dc_device': device_config.get('device'),
            'dc_legacy_mode': to_boolean(device_config.get('legacy_mode')),
            'dc_location': device_config.get('location'),
            'setSR': id_from_ref(properties.get('SR')),
            }

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

    def xenrrd_prefix(self):
        '''
        Return prefix under which XenServer stores RRD data about this
        component.
        '''
        # This is a guess at future support. XenServer 6.2 doesn't have
        # any RRD data for PBDs.
        host_uuid = self.host().xenapi_uuid
        if host_uuid and self.xenapi_uuid:
            return ('host', host_uuid, '_'.join(('pbd', self.xenapi_uuid)))

    def getIconPath(self):
        '''
        Return URL to icon representing objects of this class.
        '''
        return '/++resource++xenserver/img/virtual-disk.png'

    def server_disk(self):
        '''
        Return the server disk underlying this PBD.

        The host on which this PBD resides may also be monitored as a
        normal Linux server. Attempt to find that server and its disk
        that's associated with this PBD.
        '''
        if not self.dc_device or not self.dc_device.startswith('/dev'):
            return

        server_device = self.host().server_device()
        if server_device:
            return server_device.hw.harddisks._getOb(
                prepId(self.dc_device.replace('/dev/', '', 1)), None)


class IPBDInfo(IPooledComponentInfo):
    '''
    API Info interface for PBD.
    '''

    host = schema.Entity(title=_t(u'Host'))
    sr = schema.Entity(title=_t(u'Storage Repository'))
    server_disk = schema.Entity(title=_t(u'Server Disk'))

    currently_attached = schema.Bool(title=_t(u'Currently Attached'))
    dc_device = schema.TextLine(title=_t(u'Device Name'))
    dc_legacy_mode = schema.Bool(title=_t(u'Legacy Mode'))
    dc_location = schema.TextLine(title=_t(u'Location'))


class PBDInfo(PooledComponentInfo):
    '''
    API Info adapter factory for PBD.
    '''

    implements(IPBDInfo)
    adapts(PBD)

    host = RelationshipInfoProperty('host')
    sr = RelationshipInfoProperty('sr')
    server_disk = RelationshipInfoProperty('server_disk')

    currently_attached = ProxyProperty('currently_attached')
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
