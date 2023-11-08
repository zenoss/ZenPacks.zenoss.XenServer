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

import calendar
import collections
import math
import re
import time

from cStringIO import StringIO
from lxml import etree

from twisted.internet.defer import inlineCallbacks, returnValue

from Products.ZenModel.MinMaxThreshold import rpneval

from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource import \
    PythonDataSourcePlugin

from ZenPacks.zenoss.XenServer.modeler.incremental import DataMapProducer
from ZenPacks.zenoss.XenServer.utils import add_local_lib_path

# Allows txxenapi to be imported.
add_local_lib_path()

import txxenapi


# Module stash for clients. Allows sharing authenticated sessions.
clients = {}


def get_client(addresses, username, password):
    '''
    Return a client. From the cache of existing clients if possible.
    '''
    client_key = (tuple(addresses), username, password)

    global clients
    if client_key not in clients:
        clients[client_key] = txxenapi.Client(
            addresses, username, password)

    return clients[client_key]


def get_event(config, message, severity):
    '''
    Return an event dictionary.
    '''
    eventKey = 'XenServerCollection'
    eventClassKey = ''.join((eventKey, 'Error' if severity else 'Success'))

    return {
        'device': config.id,
        'eventKey': eventKey,
        'summary': message,
        'severity': severity,
        'eventClassKey': eventClassKey,
        }


def aggregate_values(datapoint, columns):
    '''
    Return column values aggregated according to datapoint configuration.
    '''
    aggregate = {
        'AVERAGE': lambda x: sum(x) / len(x),
        'MAX': max,
        'MIN': min,
        'SUM': sum,
        }

    return aggregate[datapoint.group_aggregation]([
        aggregate[datapoint.time_aggregation](x) for x in columns])


class BasePlugin(PythonDataSourcePlugin):
    '''
    Abstract base class for functionality common to XenServer datasource
    plugins.
    '''

    proxy_attributes = [
        'xenserver_addresses',
        'zXenServerUsername',
        'zXenServerPassword',
        ]

    def collect(self, config):
        ds0 = config.datasources[0]

        client = get_client(
            ds0.xenserver_addresses,
            ds0.zXenServerUsername,
            ds0.zXenServerPassword)

        return self.collect_xen(config, ds0, client)

    def onError(self, error, config):
        global clients
        ds0 = config.datasources[0]
        client_key =  (tuple(ds0.xenserver_addresses), ds0.zXenServerUsername, ds0.zXenServerPassword)
        if client_key in clients:
            del clients[client_key]
        return

class XenAPIPlugin(BasePlugin):
    '''
    Collects XenServer XenAPI datasources.
    '''

    @classmethod
    def config_key(cls, datasource, context):
        return BasePlugin.config_key(datasource, context) + (
            datasource.xenapi_classname,
            )

    @classmethod
    def params(cls, datasource, context):
        return {
            'xenapi_classname': datasource.talesEval(datasource.xenapi_classname, context),
            'xenapi_ref': datasource.talesEval(datasource.xenapi_ref, context),
            }

    def collect_xen(self, config, ds0, client):
        return client.xenapi[ds0.params['xenapi_classname']].get_all_records()

    def onSuccess(self, results, config):
        # Create of map of ref to datasource.
        datasources = dict(
            (x.params['xenapi_ref'], x) for x in config.datasources)

        data = self.new_data()

        for ref, properties in results.iteritems():
            datasource = datasources.get(ref)
            if not datasource:
                # We're not monitoring whatever this thing is. Skip it.
                continue

            points = dict((x.path, x) for x in datasource.points)

            for path, point in points.items():
                value = properties.get(path)

                if value is None:
                    continue

                if point.rpn:
                    try:
                        value = rpneval(value, point.rpn)
                    except Exception:
                        LOG.exception('Failed to evaluate RPN: %s', point.rpn)
                        continue

                data['values'][datasource.component][point.id] = (value, 'N')

                # Prune points so we know what's missing.
                del(points[path])

            if points:
                LOG.debug(
                    "missing values for %s:%s:%s %s",
                    config.id,
                    datasource.component,
                    datasource.datasource,
                    points.keys())

            # Prune datasources so we know what's missing.
            del(datasources[ref])

        if datasources:
            LOG.debug(
                "missing XenAPI data for %s:%s %s",
                config.id,
                config.datasources[0].params['xenapi_classname'],
                datasources.keys())

        LOG.debug(
            'success for %s XenAPI %s',
            config.id,
            config.datasources[0].params['xenapi_classname'])

        data['events'].append(get_event(config, 'successful collection', 0))

        return data

    def onError(self, error, config):
        super(XenAPIPlugin, self).onError(error, config)
        if hasattr(error, 'value'):
            error = error.value

        LOG.error(
            'error for %s XenAPI %s: %s',
            config.id,
            config.datasources[0].params['xenapi_classname'],
            error)
        
        data = self.new_data()
        data['events'].append(get_event(config, str(error), 5))
        return data


class XenAPIEventsPlugin(BasePlugin):
    '''
    Collect model updates from the XenAPI events API.
    '''

    @inlineCallbacks
    def collect_xen(self, config, ds0, client):
        if not hasattr(self, 'producer'):
            self.producer = DataMapProducer(client)

        maps = yield self.producer.getmaps()

        data = self.new_data()
        data['maps'].extend(maps)

        returnValue(data)

    def onSuccess(self, data, config):
        LOG.debug('success for %s events', config.id)
        data['events'].append(get_event(config, 'successful collection', 0))
        return data

    def onError(self, error, config):
        super(XenAPIEventsPlugin, self).onError(error, config)
        if hasattr(error, 'value'):
            error = error.value
        
        LOG.error('error for %s events: %s', config.id, error)
        data = self.new_data()
        data['events'].append(get_event(config, str(error), 5))
        return data


class XenAPIMessagesPlugin(BasePlugin):
    '''
    Collect events from the XenAPI messages API.
    '''

    proxy_attributes = BasePlugin.proxy_attributes + [
        'open_message_clear_tuples',
        ]

    @inlineCallbacks
    def collect_xen(self, config, ds0, client):
        message_api = client.xenapi.message

        # According to the following thread, this severity map is only
        # applicable to XenServer >= 6.2. Prior to that the message
        # priorities were a crapshoot.
        #
        # https://lists.xenserver.org/sympa/arc/xs-devel/2013-11/msg00004.html
        severity_map = {
            '1': 5,  # Data-loss imminent. Take action now or your data may be permanently lost (e.g. corrupted)
            '2': 4,  # Service-loss imminent. Take action now or some service(s) may fail (e.g. host / VM crash)
            '3': 3,  # Service degraded. Take action now or some service may suffer (e.g. NIC bond degraded without HA)
            '4': 2,  # Service recovered. Notice that something just improved (e.g. NIC bond repaired)
            '5': 2,  # Informational. More day-to-day stuff (e.g. VM started, suspended, shutdown, rebooted etc).
            }

        eventClassKey = 'XenServerMessage'

        data = self.new_data()
        open_message_clear_tuples = set()
        messages = yield message_api.get_all_records()

        for ref, message in messages.iteritems():
            device = config.id
            component = message.get('obj_uuid', '')
            eventKey = message.get('uuid', '')

            summary = message.get('body') or \
                message.get('name') or \
                'no body or name provided'

            severity = severity_map.get(message.get('priority', '5'), 2)

            timestamp = message['timestamp'].value.split('Z')[0]
            rcvtime = calendar.timegm(
                time.strptime(timestamp, '%Y%m%dT%H:%M:%S'))

            clear_tuple = (device, component, eventKey)
            open_message_clear_tuples.add(clear_tuple)

            # Send the event if it hasn't already been sent.
            if clear_tuple not in ds0.open_message_clear_tuples:
                data['events'].append({
                    'device': device,
                    'component': component,
                    'summary': summary,
                    'severity': severity,
                    'eventKey': eventKey,
                    'eventClassKey': eventClassKey,
                    'rcvtime': rcvtime,
                    'xenserver_name': message.get('name'),
                    'xenserver_cls': message.get('cls'),
                    'xenserver_obj_uuid': component,
                    })

        # Send clear events for events that still exist in Zenoss, but
        # have been dismissed in XenCenter.
        dismissed_clear_tuples = (
            ds0.open_message_clear_tuples - open_message_clear_tuples)

        for device, component, eventKey in dismissed_clear_tuples:
            data['events'].append({
                'device': device,
                'component': component,
                'eventKey': eventKey,
                'summary': 'message dismissed',
                'severity': 0,
                'eventClassKey': eventClassKey,
                })

        # Update this task's record of open clear tuples for the next
        # collection cycle.
        ds0.open_message_clear_tuples = open_message_clear_tuples

        returnValue(data)

    def onSuccess(self, data, config):
        LOG.debug('success for %s messages', config.id)
        data['events'].append(get_event(config, 'successful collection', 0))
        return data

    def onError(self, error, config):
        super(XenAPIMessagesPlugin, self).onError(error, config)
        if hasattr(error, 'value'):
            error = error.value
        
        LOG.error('error for %s messages: %s', config.id, error)
        data = self.new_data()
        data['events'].append(get_event(config, str(error), 5))
        return data


class XenRRDPlugin(BasePlugin):
    '''
    Collects XenServer RRD datasources.
    '''

    @classmethod
    def params(cls, datasource, context):
        if hasattr(context, 'xenrrd_prefix'):
            return {'prefix': context.xenrrd_prefix()}

        return {}

    @inlineCallbacks
    def collect_xen(self, config, ds0, client):
        rrd_tree = collections.defaultdict(
            lambda: collections.defaultdict(
                lambda: collections.defaultdict(
                    list)))

        for address in ds0.xenserver_addresses:

            # We must check what time the host thinks it is so we be
            # accurate and efficient about what and how much data we
            # request.
            server_time = None

            time_check_result = yield client.rrd_updates(address, start=1e11)

            for _, end in etree.iterparse(StringIO(time_check_result), tag='end'):
                server_time = end.text

            if not server_time:
                continue

            # Initialize {int: str} map of column indexes to
            # their corresponding entry strings. To be used to match
            # data to datapoints.
            index_entries = None

            start = int(server_time) - ds0.cycletime - 5
            result = yield client.rrd_updates(
                address, start=start, cf='AVERAGE', host=True)
            if 'Host' == ds0.template:
                LOG.debug("Datasource XenRRDPlugin: %s API Results for Host Template: %s", config.id, result)

            for _, element in etree.iterparse(StringIO(result)):
                if element.tag == 'meta':
                    step = int(element.findtext('step'))

                    if ds0.cycletime % step:
                        LOG.warn(
                            "%s:%s RRD interval (%s) not evenly divisible into datasource cycle (%s). Skipping collection",
                            config.id, address, step, ds0.cycletime)

                        continue

                    # Map (type, uuid, label) tuples to column indexes.
                    index_entries = dict(
                        (i, x.text.split(':')[1:]) for i, x in enumerate(
                            element.iter('entry')))

                elif element.tag == 'row':
                    for i, v in enumerate(element.iter('v')):
                        try:
                            value = float(v.text)
                        except (TypeError, ValueError):
                            continue

                        if not math.isnan(value):
                            etype, euuid, elabel = index_entries[i]
                            rrd_tree[etype][euuid][elabel].append(value)

        data = self.new_data()
        missing_data = collections.defaultdict(list)

        for datasource in config.datasources:
            prefix = datasource.params.get('prefix')
            if not prefix:
                continue

            datasource_data = rrd_tree[prefix[0]][prefix[1]]
            for datapoint in datasource.points:
                datapoint_data = []
                for elabel in datasource_data.keys():
                    if elabel == prefix[2]:
                        datapoint_data.append(datasource_data[elabel])

                    elif elabel.startswith(prefix[2]):
                        remainder = elabel.replace(prefix[2], '', 1)
                        if re.search(datapoint.pattern, remainder):
                            datapoint_data.append(datasource_data[elabel])

                if datapoint_data:
                    value = aggregate_values(datapoint, datapoint_data)

                    if datapoint.rpn:
                        try:
                            value = rpneval(value, datapoint.rpn)
                        except Exception:
                            LOG.exception(
                                'Failed to evaluate RPN: %s',
                                datapoint.rpn)

                            continue

                    data['values'][datasource.component][datapoint.id] = (
                        value, 'N')
                else:
                    missing_data[datasource.component].append(datapoint.id)

        for component, datapoint_ids in missing_data.items():
            LOG.debug(
                "missing RRD data for %s:%s %s",
                config.id,
                component,
                datapoint_ids)

        returnValue(data)

    def onSuccess(self, data, config):
        LOG.debug('success for %s rrd_updates', config.id)
        data['events'].append(get_event(config, 'successful collection', 0))
        return data

    def onError(self, error, config):
        super(XenRRDPlugin, self).onError(error, config)
        if hasattr(error, 'value'):
            error = error.value
        
        LOG.error('error for %s rrd_updates: %s', config.id, error)
        data = self.new_data()
        data['events'].append(get_event(config, str(error), 5))
        return data
