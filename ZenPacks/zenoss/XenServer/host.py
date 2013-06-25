#LICENSE HEADER SAMPLE
from zope.interface import implements
from Products.ZenModel.ZenossSecurity import ZEN_CHANGE_DEVICE
from Products.Zuul.decorators import info
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.utils import ZuulMessageFactory as _t
from Products.ZenModel.DeviceComponent import DeviceComponent
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.Zuul.infos.component import ComponentInfo
from Products.Zuul.interfaces.component import IComponentInfo
from Products.ZenRelations.RelSchema import ToManyCont,ToOne

class host(DeviceComponent, ManagedEntity):
    meta_type = portal_type = 'host'

    Klasses = [DeviceComponent, ManagedEntity]

    supported_bootloaders = None
    API_version_minor = None
    edition = None
    external_auth_service_name = None
    name_description = None
    patches = None
    ha_statefiles = None
    hostname = None
    name_label = None
    capabilities = None
    API_version_vendor = None
    tags = None
    power_on_mode = None
    crashdumps = None
    uuid = None
    external_auth_type = None
    sched_policy = None
    other_config = None
    enabled = None
    suspend_image_sr = None
    ha_network_peers = None
    API_version_major = None
    memory_overhead = None

    _properties = ()
    for Klass in Klasses:
        _properties = _properties + getattr(Klass,'_properties', ())

    _properties = _properties + (
        {'id': 'supported_bootloaders', 'type': 'string', 'mode': 'w'},
        {'id': 'API_version_minor', 'type': 'string', 'mode': 'w'},
        {'id': 'edition', 'type': 'string', 'mode': 'w'},
        {'id': 'external_auth_service_name', 'type': 'string', 'mode': 'w'},
        {'id': 'name_description', 'type': 'string', 'mode': 'w'},
        {'id': 'patches', 'type': 'string', 'mode': 'w'},
        {'id': 'ha_statefiles', 'type': 'string', 'mode': 'w'},
        {'id': 'hostname', 'type': 'string', 'mode': 'w'},
        {'id': 'name_label', 'type': 'string', 'mode': 'w'},
        {'id': 'capabilities', 'type': 'string', 'mode': 'w'},
        {'id': 'API_version_vendor', 'type': 'string', 'mode': 'w'},
        {'id': 'tags', 'type': 'string', 'mode': 'w'},
        {'id': 'power_on_mode', 'type': 'string', 'mode': 'w'},
        {'id': 'crashdumps', 'type': 'string', 'mode': 'w'},
        {'id': 'uuid', 'type': 'string', 'mode': 'w'},
        {'id': 'external_auth_type', 'type': 'string', 'mode': 'w'},
        {'id': 'sched_policy', 'type': 'string', 'mode': 'w'},
        {'id': 'other_config', 'type': 'string', 'mode': 'w'},
        {'id': 'enabled', 'type': 'string', 'mode': 'w'},
        {'id': 'suspend_image_sr', 'type': 'string', 'mode': 'w'},
        {'id': 'ha_network_peers', 'type': 'string', 'mode': 'w'},
        {'id': 'API_version_major', 'type': 'string', 'mode': 'w'},
        {'id': 'memory_overhead', 'type': 'string', 'mode': 'w'},
        )

    _relations = ()
    for Klass in Klasses:
        _relations = _relations + getattr(Klass, '_relations', ())

    _relations = _relations + (
        ('device', ToOne(ToManyCont, 'Products.ZenModel.Device.Device', 'hosts',)),
        ('pifs', ToManyCont(ToOne, 'ZenPacks.zenoss.XenServer.PIF', 'host',)),
        )

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

class IhostInfo(IComponentInfo):
    pif_count = schema.Int(title=_t(u'Number of PIFS'))

    supported_bootloaders = schema.TextLine(title=_t(u'supported_bootloader'))
    API_version_minor = schema.TextLine(title=_t(u'API_version_minors'))
    edition = schema.TextLine(title=_t(u'editions'))
    external_auth_service_name = schema.TextLine(title=_t(u'external_auth_service_names'))
    name_description = schema.TextLine(title=_t(u'name_descriptions'))
    patches = schema.TextLine(title=_t(u'patch'))
    ha_statefiles = schema.TextLine(title=_t(u'ha_statefile'))
    hostname = schema.TextLine(title=_t(u'hostnames'))
    name_label = schema.TextLine(title=_t(u'name_labels'))
    capabilities = schema.TextLine(title=_t(u'capability'))
    API_version_vendor = schema.TextLine(title=_t(u'API_version_vendors'))
    tags = schema.TextLine(title=_t(u'tag'))
    power_on_mode = schema.TextLine(title=_t(u'power_on_modes'))
    crashdumps = schema.TextLine(title=_t(u'crashdump'))
    uuid = schema.TextLine(title=_t(u'uuids'))
    external_auth_type = schema.TextLine(title=_t(u'external_auth_types'))
    sched_policy = schema.TextLine(title=_t(u'sched_policies'))
    other_config = schema.TextLine(title=_t(u'other_configs'))
    enabled = schema.TextLine(title=_t(u'enableds'))
    suspend_image_sr = schema.TextLine(title=_t(u'suspend_image_srs'))
    ha_network_peers = schema.TextLine(title=_t(u'ha_network_peer'))
    API_version_major = schema.TextLine(title=_t(u'API_version_majors'))
    memory_overhead = schema.TextLine(title=_t(u'memory_overheads'))

class hostInfo(ComponentInfo):
    implements(IhostInfo)

    supported_bootloaders = ProxyProperty('supported_bootloaders')
    API_version_minor = ProxyProperty('API_version_minor')
    edition = ProxyProperty('edition')
    external_auth_service_name = ProxyProperty('external_auth_service_name')
    name_description = ProxyProperty('name_description')
    patches = ProxyProperty('patches')
    ha_statefiles = ProxyProperty('ha_statefiles')
    hostname = ProxyProperty('hostname')
    name_label = ProxyProperty('name_label')
    capabilities = ProxyProperty('capabilities')
    API_version_vendor = ProxyProperty('API_version_vendor')
    tags = ProxyProperty('tags')
    power_on_mode = ProxyProperty('power_on_mode')
    crashdumps = ProxyProperty('crashdumps')
    uuid = ProxyProperty('uuid')
    external_auth_type = ProxyProperty('external_auth_type')
    sched_policy = ProxyProperty('sched_policy')
    other_config = ProxyProperty('other_config')
    enabled = ProxyProperty('enabled')
    suspend_image_sr = ProxyProperty('suspend_image_sr')
    ha_network_peers = ProxyProperty('ha_network_peers')
    API_version_major = ProxyProperty('API_version_major')
    memory_overhead = ProxyProperty('memory_overhead')


    @property
    def pif_count():
        # Using countObjects is fast.
        try:
            return self._object.pifs.countObjects()
        except:
            # Using len on the results of calling the relationship is slow.
            return len(self._object.pifs())

