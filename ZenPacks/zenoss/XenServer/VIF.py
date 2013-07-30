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
    updateToOne,
    )


class VIF(PooledComponent):
    '''
    Model class for VIF (virtual interface.)
    '''

    meta_type = portal_type = 'XenServerVIF'

    status_code = None
    status_detail = None
    MAC = None
    MTU = None
    qos_algorithm_type = None

    _properties = PooledComponent._properties + (
        {'id': 'status_code', 'type': 'string', 'mode': 'w'},
        {'id': 'status_detail', 'type': 'string', 'mode': 'w'},
        {'id': 'MAC', 'type': 'string', 'mode': 'w'},
        {'id': 'MTU', 'type': 'string', 'mode': 'w'},
        {'id': 'qos_algorithm_type', 'type': 'string', 'mode': 'w'},
        )

    _relations = PooledComponent._relations + (
        ('vm', ToOne(ToManyCont, MODULE_NAME['VM'], 'vifs')),
        ('network', ToOne(ToMany, MODULE_NAME['Network'], 'vifs')),
        )

    def getNetwork(self):
        '''
        Return network id or None.

        Used by modeling.
        '''
        obj = self.network()
        if obj:
            return obj.id

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


class IVIFInfo(IPooledComponentInfo):
    '''
    API Info interface for VIF.
    '''

    status_code = schema.TextLine(title=_t(u'status_codes'))
    status_detail = schema.TextLine(title=_t(u'status_details'))
    MAC = schema.TextLine(title=_t(u'MACS'))
    MTU = schema.TextLine(title=_t(u'MTUS'))
    qos_algorithm_type = schema.TextLine(title=_t(u'qos_algorithm_types'))


class VIFInfo(PooledComponentInfo):
    '''
    API Info adapter factory for VIF.
    '''

    implements(IVIFInfo)
    adapts(VIF)

    status_code = ProxyProperty('status_code')
    status_detail = ProxyProperty('status_detail')
    MAC = ProxyProperty('MAC')
    MTU = ProxyProperty('MTU')
    qos_algorithm_type = ProxyProperty('qos_algorithm_type')


class VIFPathReporter(DefaultPathReporter):
    '''
    Path reporter for VIF.
    '''

    def getPaths(self):
        paths = super(VIFPathReporter, self).getPaths()

        network = self.context.network()
        if network:
            paths.extend(relPath(network, 'endpoint'))

        return paths
