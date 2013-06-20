###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011, 2012 Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

import logging
LOG = logging.getLogger('zen.XenServer')

from twisted.internet import defer

from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap

from ZenPacks.zenoss.XenServer.utils import addLocalLibPath
from ZenPacks.zenoss.XenServer.lib import XenAPI

from pprint import pprint, pformat
addLocalLibPath()


def fetch_from_xen(sx):
    all_hosts = sx.host.get_all_records()
    all_host_cpus = sx.host_cpu.get_all_records()
    all_VMs = sx.VM.get_all_records()              # A dictionary of virtual machines
    all_VDIs = sx.VDI.get_all_records()              # A dictionary of virtual disk images
    all_VIFs = sx.VIF.get_all_records()              # A dictionary of virtual network interfaces
    all_PIFs = sx.PIF.get_all_records()              # A dictionary of virtual network interfaces
    all_SRs = sx.SR.get_all_records()              # A dictionary of virtual network interfaces
    
    real_VMs = [ x for x in all_VMs if not all_VMs[x]['is_a_template'] and not all_VMs[x]['is_control_domain'] ]

    for vm in real_VMs:
        del real_VMs[vm]['last_booted_record']
    
    return {
        'VMs':      real_VMs, 
        'VDIs':     all_VDIs, 
        'VIFs':     all_VIFs,
        'PIFs':     all_PIFs,
        'hosts':    all_hosts,
        'host_cpus':    all_host_cpus,
        'SRs':      all_SRs,
    }


class XenServer(PythonPlugin):
    deviceProperties = PythonPlugin.deviceProperties + (
        'zXenServerHostname',
        'zXenServerUsername',
        'zXenServerPassword',
        'zXenServerSSL',
        )

    def collect(self, device, unused):
        # if not device.zXenServerHostname:
        #     LOG.error('zXenServerHostname is not set. Not discovering')
        #     return None

        # if not device.zXenServerUsername:
        #     LOG.error('zXenServerUsername is not set. Not discovering')
        #     return None

        # if not device.zXenServerPassword:
        #     LOG.error('zXenServerPassword is not set. Not discovering')
        #     return None

        # if not device.zXenServerSSL:
        #     LOG.error('zXenServerSSL is not set. Not discovering')
        #     return None

        if device.has_attr('zXenServerHostname'):
            session = XenAPI.Session(device.zXenServerHostname)
        else:
            session = XenAPI.Session('http://%s' % device.manageIp)
        # session.xenapi.login_with_password(device.zXenServerUsername, device.zXenServerPassword)
        session.xenapi.login_with_password('root', 'zenoss') # FIXME 
        client = session.xenapi

        d = DeferredList((
            fetch_from_xen(client),
            ), consumeErrors=True).addCallback(self.process)

        return d

    def process(self, device, results, unused):
        # See https://dev.zenoss.com/tracint/browser/trunk/enterprise/zenpacks/ZenPacks.zenoss.EMC.base/ZenPacks/zenoss/EMC/base/modeler/emc.py
    
        pprint(results)

        log.info('Modeler %s processing data for server %s',
            self.name(), device.id)

        _om = ObjectMap()

        maps = []

        # ObjectMap lists.
        hosts_oms = []

        # ObjectMap lists in dictionaries with compname as key.
        map_hosts_oms = collections.defaultdict(list)

        maps.append(RelationshipMap(
            relname="hosts",
            compname="os",
            modname="ZenPacks.zenoss.XenServer.base.host",
            objmaps=hosts_oms))

        return maps
