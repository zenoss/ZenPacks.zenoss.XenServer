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


class PIF(BaseComponent):
    '''
    Model class for PIF (physical interface.)
    '''
    meta_type = portal_type = 'XenServerPIF'

    IP = None
    MAC = None
    netmask = None
    gateway = None

    _properties = BaseComponent._properties + (
        {'id': 'IP', 'type': 'string', 'mode': 'w'},
        {'id': 'MAC', 'type': 'string', 'mode': 'w'},
        {'id': 'netmask', 'type': 'string', 'mode': 'w'},
        {'id': 'gateway', 'type': 'string', 'mode': 'w'},
        )

    _relations = BaseComponent._relations + (
        ('host', ToOne(ToManyCont, MODULE_NAME['Host'], 'pifs')),
        ('network', ToOne(ToMany, MODULE_NAME['Network'], 'pifs')),
        )

    def getNetwork(self):
        '''
        Return network id or None.

        Used by modeling.
        '''
        network = self.network()
        if network:
            return network.id

    def setNetwork(self, network_id):
        '''
        Set network by id.

        Used by modeling.
        '''
        updateToOne(
            relationship=self.network,
            root=self.device(),
            type_=CLASS_NAME['Network'],
            id_=network_id)


class IPIFInfo(IBaseComponentInfo):
    '''
    API Info interface for PIF.
    '''

    IP = schema.TextLine(title=_t(u'IPS'))
    MAC = schema.TextLine(title=_t(u'MACS'))
    netmask = schema.TextLine(title=_t(u'netmasks'))
    gateway = schema.TextLine(title=_t(u'gateways'))


class PIFInfo(BaseComponentInfo):
    '''
    API Info adapter factor for PIF.
    '''

    implements(IPIFInfo)
    adapts(PIF)

    IP = ProxyProperty('IP')
    MAC = ProxyProperty('MAC')
    netmask = ProxyProperty('netmask')
    gateway = ProxyProperty('gateway')


class PIFPathReporter(DefaultPathReporter):
    '''
    Path reporter for PIF.
    '''

    def getPaths(self):
        paths = super(PIFPathReporter, self).getPaths()

        network = self.context.network()
        if network:
            paths.extend(relPath(network, 'endpoint'))

        return paths
