##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

'''
Twisted library for working with the XenServer XenAPI.

    http://docs.vmd.citrix.com/XenServer/6.2.0/1.0/en_gb/api/
'''

import collections
import logging
import random

from twisted.internet import reactor
from twisted.internet.defer import Deferred, inlineCallbacks, returnValue
from twisted.web import xmlrpc
from twisted.web.client import getPage


__all__ = ['Client']

LOG = logging.getLogger('txxenapi')


XENAPI_CLASSNAMES = [
    'host',
    'host_cpu',
    'host_metrics',
    'network',
    'PBD',
    'PIF',
    'PIF_metrics',
    'pool',
    'SR',
    'VBD',
    'VBD_metrics',
    'VDI',
    'VIF',
    'VIF_metrics',
    'VM',
    'VM_appliance',
    'VM_guest_metrics',
    'VM_metrics',
    ]


class Client(object):
    '''
    XenServer XenAPI client.
    '''

    _addresses = None
    _username = None
    _password = None
    _proxy = None
    _session_key = None

    def __init__(self, addresses, username, password):
        '''
        Create a XenAPI client.

        addresses should ideally be a list of resolvable hostnames or
        IP addresses for all XenServers in a pool. For less durable
        requirements a single resolvable hostname or IP address for
        the pool's current master will work.
        '''
        if isinstance(addresses, basestring):
            addresses = [addresses]

        self._addresses = collections.deque(addresses)
        self._username = username
        self._password = password

    def set_server(self, address):
        '''
        Specify the XenServer explicitely.

        This will be called automatically if the current XenServer
        responds with a HOST_IS_SLAVE status. The server will be set to
        the new master specified in the response.
        '''
        if address not in self._addresses:
            self._addresses.append(address)

        self._proxy = xmlrpc.Proxy('https://%s/' % address, allowNone=None)

    def rotate_server(self):
        '''
        Rotate to next XenServer in list of addresses.

        This will be called automatically if the client is configured
        with more than one address, and that address fails to respond.
        '''
        self.set_server(self._addresses[0])
        self._addresses.rotate(-1)

    @inlineCallbacks
    def _retryingCallRemote(self, method, *args):
        for retry in xrange(len(self._addresses) * 2 + 1):
            if retry > 0:
                delay = (random.random() * pow(4, retry)) / 10.0
                yield sleep(delay)

            try:
                result = yield self._proxy.callRemote(method, *args)
            except Exception:
                if len(self._addresses) > 1:
                    self.rotate_server()

                continue

            if not isinstance(result, dict):
                raise Exception("invalid response")

            if 'Status' not in result:
                raise Exception("status missing from response")

            if result['Status'] == 'Success':
                if 'Value' in result:
                    returnValue(result['Value'])
                else:
                    raise Exception("session key missing from response")

            else:
                if 'ErrorDescription' in result:
                    if isinstance(result['ErrorDescription'], list):
                        if result['ErrorDescription'][0] == 'HOST_IS_SLAVE':
                            self.set_server(result['ErrorDescription'][1])
                            continue

                    raise Exception(result['ErrorDescription'])
                else:
                    raise Exception("error with no description")

    @inlineCallbacks
    def login(self):
        '''
        Login and save the session ID for future calls.
        '''
        self._session_key = yield self._retryingCallRemote(
            'session.login_with_password', self._username, self._password)

        returnValue(self._session_key)

    @inlineCallbacks
    def callRemote(self, method, *args):
        '''
        Wrap XML-RPC callRemote to handle common results and support
        master migration.
        '''
        if not self._proxy:
            yield self.rotate_server()

        if not self._session_key:
            yield self.login()

        if args[0] is None:
            args = list(args)
            args[0] = self._session_key

        result = yield self._retryingCallRemote(method, *args)
        returnValue(result)

    def close(self):
        '''
        Logout if logged in. Return deferred.
        '''
        if self._proxy and self._session_key:
            d = self._retryingCallRemote('session.logout', self._session_key)
        else:
            d = Deferred()
            d.callback(None)

        return d

    @property
    def xenapi(self):
        '''
        XenAPI endpoint. Used to call XenAPI methods.
        '''
        return APICall(self)

    @inlineCallbacks
    def rrd_updates(self, address, start=None, cf=None, interval=None, host=None, uuid=None, json=None):
        '''
        XenServer RRDtool rrd_updates. For performance data.
        '''
        if not self._proxy:
            yield self.rotate_server()

        if not self._session_key:
            yield self.login()

        url_parts = []
        url_parts.append('https://{0}/rrd_updates?session_id={1}'.format(
            address, self._session_key))

        if start:
            url_parts.append('start={0}'.format(int(start)))

        if cf:
            url_parts.append('cf={0}'.format(cf))

        if interval:
            url_parts.append('interval={0}'.format(int(interval)))

        if host:
            url_parts.append('host')

        if uuid:
            url_parts.append('uuid={0}'.format(uuid))

        if json:
            url_parts.append('json')

        result = yield getPage('&'.join(url_parts))
        returnValue(result)


class APICall(object):
    '''
    Idiomatic wrapper around Client.callRemote.
    '''

    def __init__(self, client, name=None):
        self._client = client
        self._name = name

    def __getattr__(self, name):
        if self._name:
            return APICall(self._client, '{0}.{1}'.format(self._name, name))
        else:
            return APICall(self._client, name)

    def __getitem__(self, name):
        return getattr(self, name)

    def __call__(self, *args):
        return self._client.callRemote(self._name, self._client._session_key, *args)


def sleep(seconds):
    '''
    Return a deferred that is called in given seconds.
    '''
    d = Deferred()
    reactor.callLater(seconds, d.callback, None)
    return d


if __name__ == '__main__':
    import pprint
    import sys

    @inlineCallbacks
    def main(address, username, password, xenapi_classnames):
        client = Client([address], username, password)

        for xenapi_classname in xenapi_classnames:
            try:
                r = yield getattr(client.xenapi, xenapi_classname).get_all_records()
            except Exception, ex:
                print >> sys.stderr, ex
                continue

            if len(xenapi_classnames) > 1:
                filename = '{0}.py'.format(xenapi_classname)
                print "Writing {0}.".format(filename)
                with open(filename, 'w') as f:
                    pprint.pprint(r, f)
            else:
                pprint.pprint(r)

        yield client.close()

        reactor.stop()

    if len(sys.argv) < 5:
        print >> sys.stderr, (
            "Usage: {0} <address> <username> <password> [all|class]".format(
                sys.argv[0]))

        sys.exit(1)

    xenapi_classnames = sys.argv[4:]

    if 'all' in xenapi_classnames:
        main(sys.argv[1], sys.argv[2], sys.argv[3], XENAPI_CLASSNAMES)
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3], xenapi_classnames)

    reactor.run()
