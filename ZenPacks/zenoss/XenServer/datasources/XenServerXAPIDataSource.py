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


class XenServerXAPIDataSource(PythonDataSource):
    '''
    Datasource used to define XAPI requests for monitoring data.
    '''

    ZENPACKID = 'ZenPacks.zenoss.XenServer'

    sourcetypes = ('XenServer XAPI',)
    sourcetype = sourcetypes[0]

    # RRDDataSource
    component = '${here/id}'
    cycletime = '${here/zXenServerCollectionInterval}'
    eventClass = '/Ignore'
    severity = 0

    # PythonDataSource
    plugin_classname = 'ZenPacks.zenoss.XenServer.datasource_plugins.XenServerXAPIDataSourcePlugin'

    # XenServerXAPIDataSource
    xapi_classname = ''
    xapi_ref = '${here/xapi_ref}'

    _properties = PythonDataSource._properties + (
        {'id': 'xapi_classname', 'type': 'string'},
        {'id': 'xapi_ref', 'type': 'string'},
        )

    def getDescription(self):
        '''
        Return short string that represents this datasource.
        '''
        return self.xapi_classname

    def manage_addRRDDataPoint(self, id, REQUEST=None):
        '''
        Add datapoint to this datasource.

        Overridden to create XenServerXAPIDataPoint datapoints.
        '''
        if not id:
            return self.callZenScreen(REQUEST)

        id = self.prepId(id)
        self.datapoints._setObject(id, XenServerXAPIDataPoint(id))
        datapoint = self.datapoints._getOb(id)
        if REQUEST:
            if datapoint:
                url = '%s/datapoints/%s' % (self.getPrimaryUrlPath(), datapoint.id)
                REQUEST['RESPONSE'].redirect(url)
            return self.callZenScreen(REQUEST)

        return datapoint


class IXenServerXAPIDataSourceInfo(IRRDDataSourceInfo):
    '''
    API Info interface for XenServerXAPIDataSource.
    '''

    xapi_classname = schema.TextLine(
        group=_t(u'XenServer'),
        title=_t(u'XAPI Class Name'))

    xapi_ref = schema.TextLine(
        group=_t(u'XenServer'),
        title=_t(u'XAPI Reference'))


class XenServerXAPIDataSourceInfo(RRDDataSourceInfo):
    '''
    API Info adapter factory for XenServerXAPIDataSource.
    '''

    implements(IXenServerXAPIDataSourceInfo)
    adapts(XenServerXAPIDataSource)

    testable = False

    xapi_classname = ProxyProperty('xapi_classname')
    xapi_ref = ProxyProperty('xapi_ref')


class XenServerXAPIDataPoint(RRDDataPoint):
    '''
    Datapoint used to define values to capture from XenAPI responses.

    This datapoint will only ever be used by XenServerXAPIDataSource.
    '''

    path = None
    rpn = None

    _properties = RRDDataPoint._properties + (
        {'id': 'path', 'type': 'string', 'mode': 'w'},
        {'id': 'rpn', 'type': 'string', 'mode': 'w'},
        )


class IXenServerXAPIDataPointInfo(IDataPointInfo):
    '''
    API Info interface for XenServerXAPIDataPoint.
    '''

    path = schema.TextLine(title=_t(u'Path'))
    rpn = schema.TextLine(title=_t(u'RPN'))


class XenServerXAPIDataPointInfo(DataPointInfo):
    '''
    API Info adapter factory for XenServerXAPIDataPoint.
    '''

    implements(IXenServerXAPIDataPointInfo)
    adapts(XenServerXAPIDataPoint)

    path = ProxyProperty('path')
    rpn = ProxyProperty('rpn')
