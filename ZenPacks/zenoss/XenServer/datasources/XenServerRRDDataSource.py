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


class XenServerRRDDataSource(PythonDataSource):
    '''
    Datasource used to define XenAPI requests for monitoring data.
    '''

    ZENPACKID = 'ZenPacks.zenoss.XenServer'

    sourcetypes = ('XenServer RRD',)
    sourcetype = sourcetypes[0]

    # RRDDataSource
    component = '${here/id}'
    cycletime = 300
    eventClass = '/Ignore'
    severity = 0

    # PythonDataSource
    plugin_classname = 'ZenPacks.zenoss.XenServer.datasource_plugins.XenServerRRDDataSourcePlugin'

    def getDescription(self):
        '''
        Return short string that represents this datasource.
        '''
        return "XenServer (rrd_updates)"

    def manage_addRRDDataPoint(self, id, REQUEST=None):
        '''
        Add datapoint to this datasource.

        Overridden to create XenServerDatapoint datapoints.
        '''
        if not id:
            return self.callZenScreen(REQUEST)

        id = self.prepId(id)
        self.datapoints._setObject(id, XenServerRRDDataPoint(id))
        datapoint = self.datapoints._getOb(id)
        if REQUEST:
            if datapoint:
                url = '%s/datapoints/%s' % (self.getPrimaryUrlPath(), datapoint.id)
                REQUEST['RESPONSE'].redirect(url)
            return self.callZenScreen(REQUEST)

        return datapoint


class IXenServerRRDDataSourceInfo(IRRDDataSourceInfo):
    '''
    API Info interface for XenServerRRDDataSource.
    '''


class XenServerRRDDataSourceInfo(RRDDataSourceInfo):
    '''
    API Info adapter factory for XenServerRRDDataSource.
    '''

    implements(IXenServerRRDDataSourceInfo)
    adapts(XenServerRRDDataSource)

    testable = False

    cycletime = ProxyProperty('cycletime')


class XenServerRRDDataPoint(RRDDataPoint):
    '''
    Datapoint used to define values to capture from XenAPI responses.

    This datapoint will only ever be used by XenServerRRDDataSource.
    '''

    pattern = ''
    rpn = ''
    time_aggregation = 'AVERAGE'
    group_aggregation = 'AVERAGE'

    _properties = RRDDataPoint._properties + (
        {'id': 'pattern', 'type': 'string', 'mode': 'w'},
        {'id': 'rpn', 'type': 'string', 'mode': 'w'},
        {'id': 'time_aggregation', 'type': 'string', 'mode': 'w'},
        {'id': 'group_aggregation', 'type': 'string', 'mode': 'w'},
        )


class IXenServerRRDDataPointInfo(IDataPointInfo):
    '''
    API Info interface for XenServerRRDDataPoint.
    '''

    pattern = schema.TextLine(title=_t(u'XenServer RRD Pattern'))
    rpn = schema.TextLine(title=_t(u'XenServer RRD RPN'))
    time_aggregation = schema.TextLine(title=_t(u'XenServer RRD Time Aggregation'))
    group_aggregation = schema.TextLine(title=_t(u'XenServer RRD Group Aggregation'))


class XenServerRRDDataPointInfo(DataPointInfo):
    '''
    API Info adapter factory for XenServerRRDDataPoint.
    '''

    implements(IXenServerRRDDataPointInfo)
    adapts(XenServerRRDDataPoint)

    pattern = ProxyProperty('pattern')
    rpn = ProxyProperty('rpn')
    time_aggregation = ProxyProperty('time_aggregation')
    group_aggregation = ProxyProperty('group_aggregation')
