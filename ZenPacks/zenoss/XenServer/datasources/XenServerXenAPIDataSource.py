##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import logging
LOG = logging.getLogger('zen.XenServer')

from zope.component import adapts
from zope.interface import implements

from Products.ZenModel.RRDDataPoint import RRDDataPoint
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.template import DataPointInfo, RRDDataSourceInfo
from Products.Zuul.interfaces import IDataPointInfo, IRRDDataSourceInfo
from Products.Zuul.utils import ZuulMessageFactory as _t

from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource \
    import PythonDataSource


class XenServerXenAPIDataSource(PythonDataSource):
    '''
    Datasource used to define XenAPI requests for monitoring data.
    '''

    ZENPACKID = 'ZenPacks.zenoss.XenServer'

    sourcetypes = ('XenServer XenAPI',)
    sourcetype = sourcetypes[0]

    # RRDDataSource
    component = '${here/id}'
    cycletime = '${here/zXenServerPerfInterval}'
    eventClass = '/Ignore'
    severity = 0

    # PythonDataSource
    plugin_classname = 'ZenPacks.zenoss.XenServer.datasource_plugins.XenAPIPlugin'

    # XenServerXenAPIDataSource
    xenapi_classname = ''
    xenapi_ref = '${here/xenapi_ref}'

    _properties = PythonDataSource._properties + (
        {'id': 'xenapi_classname', 'type': 'string'},
        {'id': 'xenapi_ref', 'type': 'string'},
        )

    def getDescription(self):
        '''
        Return short string that represents this datasource.
        '''
        return self.xenapi_classname

    def manage_addRRDDataPoint(self, id, REQUEST=None):
        '''
        Add datapoint to this datasource.

        Overridden to create XenServerXenAPIDataPoint datapoints.
        '''
        if not id:
            return self.callZenScreen(REQUEST)

        id = self.prepId(id)
        self.datapoints._setObject(id, XenServerXenAPIDataPoint(id))
        datapoint = self.datapoints._getOb(id)
        if REQUEST:
            if datapoint:
                url = '%s/datapoints/%s' % (self.getPrimaryUrlPath(), datapoint.id)
                REQUEST['RESPONSE'].redirect(url)
            return self.callZenScreen(REQUEST)

        return datapoint


class IXenServerXenAPIDataSourceInfo(IRRDDataSourceInfo):
    '''
    API Info interface for XenServerXenAPIDataSource.
    '''

    xenapi_classname = schema.TextLine(
        group=_t(u'XenServer'),
        title=_t(u'XenAPI Class Name'))

    xenapi_ref = schema.TextLine(
        group=_t(u'XenServer'),
        title=_t(u'XenAPI Reference'))


class XenServerXenAPIDataSourceInfo(RRDDataSourceInfo):
    '''
    API Info adapter factory for XenServerXenAPIDataSource.
    '''

    implements(IXenServerXenAPIDataSourceInfo)
    adapts(XenServerXenAPIDataSource)

    testable = False

    xenapi_classname = ProxyProperty('xenapi_classname')
    xenapi_ref = ProxyProperty('xenapi_ref')


class XenServerXenAPIDataPoint(RRDDataPoint):
    '''
    Datapoint used to define values to capture from XenAPI responses.

    This datapoint will only ever be used by XenServerXenAPIDataSource.
    '''

    path = None
    rpn = None

    _properties = RRDDataPoint._properties + (
        {'id': 'path', 'type': 'string', 'mode': 'w'},
        {'id': 'rpn', 'type': 'string', 'mode': 'w'},
        )


class IXenServerXenAPIDataPointInfo(IDataPointInfo):
    '''
    API Info interface for XenServerXenAPIDataPoint.
    '''

    path = schema.TextLine(title=_t(u'Path'))
    rpn = schema.TextLine(title=_t(u'RPN'))


class XenServerXenAPIDataPointInfo(DataPointInfo):
    '''
    API Info adapter factory for XenServerXenAPIDataPoint.
    '''

    implements(IXenServerXenAPIDataPointInfo)
    adapts(XenServerXenAPIDataPoint)

    path = ProxyProperty('path')
    rpn = ProxyProperty('rpn')
