(function(){

/*** DeviceOverviewPanel Changes ********************************************/

Ext.onReady(function(){
    /* Summary Panel Override */
    var DEVICE_SUMMARY_PANEL = 'deviceoverviewpanel_summary';
    Ext.ComponentMgr.onAvailable(DEVICE_SUMMARY_PANEL, function(){
        var summarypanel = Ext.getCmp(DEVICE_SUMMARY_PANEL);
        summarypanel.removeField('uptime');
        summarypanel.removeField('memory');
    });

    /* ID Panel Override */
    var DEVICE_ID_PANEL = 'deviceoverviewpanel_idsummary';
    Ext.ComponentMgr.onAvailable(DEVICE_ID_PANEL, function(){
        var idpanel = Ext.getCmp(DEVICE_ID_PANEL);

        idpanel.removeField('serialNumber');
    });

    /* Description Panel Override */
    var DEVICE_DESCRIPTION_PANEL = 'deviceoverviewpanel_descriptionsummary';
    Ext.ComponentMgr.onAvailable(DEVICE_DESCRIPTION_PANEL, function(){
        var descriptionpanel = Ext.getCmp(DEVICE_DESCRIPTION_PANEL);
        descriptionpanel.removeField('rackSlot');
        descriptionpanel.removeField('hwManufacturer');
        descriptionpanel.removeField('hwModel');
    });

    /* SNMP Panel Override */
    var DEVICE_SNMP_PANEL = 'deviceoverviewpanel_snmpsummary';
    Ext.ComponentMgr.onAvailable(DEVICE_SNMP_PANEL, function(){
        var snmppanel = Ext.getCmp(DEVICE_SNMP_PANEL);
        snmppanel.hide();
    });
});


/*** Component Panel Support ************************************************/

var ZC = Ext.ns('Zenoss.component');

Ext.apply(Zenoss.render, {
    xenserver_entityLinkFromGrid: function(obj, col, record) {
        if (!obj)
            return;

        if (typeof(obj) == 'string')
            obj = record.data;

        if (!obj.title && obj.name)
            obj.title = obj.name;

        var isLink = false;

        if (this.refName == 'componentgrid') {
            // Zenoss >= 4.2 / ExtJS4
            if (this.subComponentGridPanel || this.componentType != obj.meta_type)
                isLink = true;
        } else {
            // Zenoss < 4.2 / ExtJS3
            if (!this.panel || this.panel.subComponentGridPanel)
                isLink = true;
        }

        if (isLink) {
            return '<a href="javascript:Ext.getCmp(\'component_card\').componentgrid.jumpToEntity(\''+obj.uid+'\', \''+obj.meta_type+'\');">'+obj.title+'</a>';
        } else {
            return obj.title;
        }
    }
});

ZC.XenServerComponentGridPanel = Ext.extend(ZC.ComponentGridPanel, {
    subComponentGridPanel: false,

    jumpToEntity: function(uid, meta_type) {
        var tree = Ext.getCmp('deviceDetailNav').treepanel;
        var tree_selection_model = tree.getSelectionModel();
        var components_node = tree.getRootNode().findChildBy(
            function(n) {
                if (n.data) {
                    // Zenoss >= 4.2 / ExtJS4
                    return n.data.text == 'Components';
                }

                // Zenoss < 4.2 / ExtJS3
                return n.text == 'Components';
            });

        var component_card = Ext.getCmp('component_card');

        if (components_node.data) {
            // Zenoss >= 4.2 / ExtJS4
            component_card.setContext(components_node.data.id, meta_type);
        } else {
            // Zenoss < 4.2 / ExtJS3
            component_card.setContext(components_node.id, meta_type);
        }

        component_card.selectByToken(uid);

        var component_type_node = components_node.findChildBy(
            function(n) {
                if (n.data) {
                    // Zenoss >= 4.2 / ExtJS4
                    return n.data.id == meta_type;
                }

                // Zenoss < 4.2 / ExtJS3
                return n.id == meta_type;
            });

        if (component_type_node.select) {
            tree_selection_model.suspendEvents();
            component_type_node.select();
            tree_selection_model.resumeEvents();
        } else {
            tree_selection_model.select([component_type_node], false, true);
        }
    }
});


/*** Component Panels *******************************************************/

ZC.XenServerHostPanel = Ext.extend(ZC.XenServerComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'XenServerHost',
            autoExpandColumn: 'name',
            sortInfo: {
                field: 'name',
                direction: 'asc'
            },
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'meta_type'},
                {name: 'status'},
                {name: 'severity'},
                {name: 'usesMonitorAttribute'},
                {name: 'pool'},
                {name: 'is_pool_master'},
                {name: 'address'},
                {name: 'cpu_count'},    // for cpu_combined
                {name: 'cpu_speed'},    // for cpu_combined
                {name: 'memory_total'},
                {name: 'vm_count'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid
            },{
                id: 'pool',
                dataIndex: 'pool',
                header: _t('Pool'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                width: 120
            },{
                id: 'is_pool_master',
                dataIndex: 'is_pool_master',
                header: _t('Master'),
                renderer: Zenoss.render.checkbox,
                width: 60
            },{
                id: 'address',
                dataIndex: 'address',
                header: _t('Address'),
                width: 90
            },{
                id: 'cpu_combined',
                dataIndex: 'cpu_count',
                header: _t('CPUs'),
                renderer: function(value, metaData, record) {
                    return '<span title="Count x Speed">' +
                        record.data.cpu_count + ' x ' +
                        Zenoss.render.cpu_speed(record.data.cpu_speed) +
                        '</span>';
                },
                width: 80
            },{
                id: 'memory_total',
                dataIndex: 'memory_total',
                header: _t('Memory'),
                renderer: Zenoss.render.memory,
                width: 70
            },{
                id: 'vm_count',
                dataIndex: 'vm_count',
                header: _t('VMs'),
                width: 50
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerHostPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('XenServerHostPanel', ZC.XenServerHostPanel);

ZC.XenServerHostCPUPanel = Ext.extend(ZC.XenServerComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'XenServerHostCPU',
            autoExpandColumn: 'modelname',
            sortInfo: {
                field: 'name',
                direction: 'asc'
            },
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'meta_type'},
                {name: 'status'},
                {name: 'severity'},
                {name: 'host'},
                {name: 'modelname'},
                {name: 'speed'},
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                width: 50
            },{
                id: 'host',
                dataIndex: 'host',
                header: _t('Host'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                width: 120
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                width: 60
            },{
                id: 'modelname',
                dataIndex: 'modelname',
                header: _t('Model')
            },{
                id: 'speed',
                dataIndex: 'speed',
                header: _t('Speed'),
                renderer: Zenoss.render.cpu_speed,
                width: 80
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerHostCPUPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('XenServerHostCPUPanel', ZC.XenServerHostCPUPanel);

Zenoss.nav.appendTo('Component', [{
    id: 'component_hostcpus',
    text: _t('Host CPUs'),
    xtype: 'XenServerHostCPUPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        return navpanel.refOwner.componentType == 'XenServerHost';
    },
    setContext: function(uid) {
        ZC.XenServerHostCPUPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

ZC.XenServerNetworkPanel = Ext.extend(ZC.XenServerComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'XenServerNetwork',
            autoExpandColumn: 'name',
            sortInfo: {
                field: 'name',
                direction: 'asc'
            },
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'meta_type'},
                {name: 'status'},
                {name: 'severity'},
                {name: 'bridge'},
                {name: 'pif_count'},
                {name: 'vif_count'},
                {name: 'is_guest_installer_network'},
                {name: 'is_host_internal_management_network'},
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid
            },{
                id: 'bridge',
                dataIndex: 'bridge',
                header: _t('Bridge'),
                width: 80
            },{
                id: 'pif_count',
                dataIndex: 'pif_count',
                header: _t('PIFs'),
                width: 60
            },{
                id: 'vif_count',
                dataIndex: 'vif_count',
                header: _t('VIFs'),
                width: 60
            },{
                id: 'is_guest_installer_network',
                dataIndex: 'is_guest_installer_network',
                header: _t('Guest Installer'),
                renderer: Zenoss.render.checkbox,
                width: 100
            },{
                id: 'is_host_internal_management_network',
                dataIndex: 'is_host_internal_management_network',
                header: _t('Management'),
                renderer: Zenoss.render.checkbox,
                width: 90
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerNetworkPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('XenServerNetworkPanel', ZC.XenServerNetworkPanel);

ZC.XenServerPBDPanel = Ext.extend(ZC.XenServerComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'XenServerPBD',
            autoExpandColumn: 'name',
            sortInfo: {
                field: 'name',
                direction: 'asc'
            },
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'meta_type'},
                {name: 'status'},
                {name: 'severity'},
                {name: 'host'},
                {name: 'sr'},
                {name: 'currently_attached'},
                {name: 'dc_legacy_mode'},
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid
            },{
                id: 'host',
                dataIndex: 'host',
                header: _t('Host'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                width: 120
            },{
                id: 'sr',
                dataIndex: 'sr',
                header: _t('Storage Repository'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                width: 120
            },{
                id: 'currently_attached',
                dataIndex: 'currently_attached',
                header: _t('Attached'),
                renderer: Zenoss.render.checkbox,
                width: 70
            },{
                id: 'dc_legacy_mode',
                dataIndex: 'dc_legacy_mode',
                header: _t('Legacy Mode'),
                renderer: Zenoss.render.checkbox,
                width: 95
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerPBDPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('XenServerPBDPanel', ZC.XenServerPBDPanel);

Zenoss.nav.appendTo('Component', [{
    id: 'component_pbds',
    text: _t('PBDs'),
    xtype: 'XenServerPBDPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'XenServerHost': return true;
            case 'XenServerSR': return true;
            default: return false;
        }
    },
    setContext: function(uid) {
        ZC.XenServerPBDPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

ZC.XenServerPIFPanel = Ext.extend(ZC.XenServerComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'XenServerPIF',
            autoExpandColumn: 'network',
            sortInfo: {
                field: 'name',
                direction: 'asc'
            },
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'meta_type'},
                {name: 'status'},
                {name: 'severity'},
                {name: 'host'},
                {name: 'network'},
                {name: 'primary_address_type'},  // for address
                {name: 'ipv4_addresses'},  // for address
                {name: 'ipv6_addresses'},  // for address
                {name: 'management'},
                {name: 'physical'},
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'gateway'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                width: 120
            },{
                id: 'host',
                dataIndex: 'host',
                header: _t('Host'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                width: 120
            },{
                id: 'network',
                dataIndex: 'network',
                header: _t('Network'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid
            },{
                id: 'address',
                dataIndex: 'ipv4_addresses',
                header: _t('Address'),
                renderer: function(value, metaData, record) {
                    if (record.data.primary_address_type == 'IPv4') {
                        if (record.data.ipv4_addresses.length > 0) {
                            return record.data.ipv4_addresses[0];
                        }
                    } else if (record.data.primary_address_type == 'IPv6') {
                        if (record.data.ipv6_addresses.length > 0) {
                            return record.dataipv6_addresses[0];
                        }
                    }
                },
                width: 90
            },{
                id: 'management',
                dataIndex: 'management',
                header: _t('Management'),
                renderer: Zenoss.render.checkbox,
                width: 85
            },{
                id: 'physical',
                dataIndex: 'physical',
                header: _t('Physical'),
                renderer: Zenoss.render.checkbox,
                width: 65
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerPIFPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('XenServerPIFPanel', ZC.XenServerPIFPanel);

Zenoss.nav.appendTo('Component', [{
    id: 'component_pifs',
    text: _t('PIFs'),
    xtype: 'XenServerPIFPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'XenServerHost': return true;
            case 'XenServerNetwork': return true;
            default: return false;
        }
    },
    setContext: function(uid) {
        ZC.XenServerPIFPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

ZC.XenServerPoolPanel = Ext.extend(ZC.XenServerComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'XenServerPool',
            autoExpandColumn: 'name',
            sortInfo: {
                field: 'name',
                direction: 'asc'
            },
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'meta_type'},
                {name: 'status'},
                {name: 'severity'},
                {name: 'master'},
                {name: 'default_sr'},
                {name: 'ha_enabled'},
                {name: 'ha_allow_overcommit'},
                {name: 'ha_host_failures_to_tolerate'},
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid
            },{
                id: 'master',
                dataIndex: 'master',
                header: _t('Master Host'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                width: 120
            },{
                id: 'default_sr',
                dataIndex: 'default_sr',
                header: _t('Default SR'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                width: 120
            },{
                id: 'ha_enabled',
                dataIndex: 'ha_enabled',
                header: _t('HA Enabled'),
                renderer: Zenoss.render.checkbox,
                width: 80
            },{
                id: 'ha_allow_overcommit',
                dataIndex: 'ha_allow_overcommit',
                header: _t('Allow Overcommit'),
                renderer: Zenoss.render.checkbox,
                width: 115
            },{
                id: 'ha_host_failures_to_tolerate',
                dataIndex: 'ha_host_failures_to_tolerate',
                header: _t('Tolerable Host Failures'),
                width: 140
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerPoolPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('XenServerPoolPanel', ZC.XenServerPoolPanel);

ZC.XenServerSRPanel = Ext.extend(ZC.XenServerComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'XenServerSR',
            autoExpandColumn: 'name',
            sortInfo: {
                field: 'name',
                direction: 'asc'
            },
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'meta_type'},
                {name: 'status'},
                {name: 'severity'},
                {name: 'content_type'},
                {name: 'sr_type'},  // for combined_type
                {name: 'sm_type'},  // for combined_type
                {name: 'physical_size'},
                {name: 'shared'},
                {name: 'local_cache_enabled'},
                {name: 'usesMonitorAttribute'},
                {name: 'pbd_count'},
                {name: 'vdi_count'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid
            },{
                id: 'content_type',
                dataIndex: 'content_type',
                header: _t('Content'),
                width: 70
            },{
                id: 'combined_type',
                dataIndex: 'sr_type',
                header: _t('Type'),
                renderer: function(value, metaData, record) {
                    if (record.data.sm_type) {
                        return record.data.sr_type +' / ' + record.data.sm_type;
                    }

                    return value;
                },
                width: 80
            },{
                id: 'physical_size',
                dataIndex: 'physical_size',
                header: _t('Size'),
                renderer: Zenoss.render.bytesString,
                width: 80
            },{
                id: 'shared',
                dataIndex: 'shared',
                header: _t('Shared'),
                renderer: Zenoss.render.checkbox,
                width: 60
            },{
                id: 'local_cache_enabled',
                dataIndex: 'local_cache_enabled',
                header: _t('Local Cache'),
                renderer: Zenoss.render.checkbox,
                width: 85
            },{
                id: 'pbd_count',
                dataIndex: 'pbd_count',
                header: _t('PBDs'),
                width: 50
            },{
                id: 'vdi_count',
                dataIndex: 'vdi_count',
                header: _t('VDIs'),
                width: 50
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerSRPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('XenServerSRPanel', ZC.XenServerSRPanel);

ZC.XenServerVBDPanel = Ext.extend(ZC.XenServerComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'XenServerVBD',
            autoExpandColumn: 'name',
            sortInfo: {
                field: 'name',
                direction: 'asc'
            },
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'meta_type'},
                {name: 'status'},
                {name: 'severity'},
                {name: 'vm'},
                {name: 'vdi'},
                {name: 'vbd_type'},
                {name: 'mode'},
                {name: 'bootable'},
                {name: 'unpluggable'},
                {name: 'currently_attached'},
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid
            },{
                id: 'vm',
                dataIndex: 'vm',
                header: _t('VM'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                width: 120
            },{
                id: 'vdi',
                dataIndex: 'vdi',
                header: _t('VDI'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                width: 120
            },{
                id: 'mode',
                dataIndex: 'mode',
                header: _t('Mode'),
                width: 80
            },{
                id: 'bootable',
                dataIndex: 'bootable',
                header: _t('Bootable'),
                renderer: Zenoss.render.checkbox,
                width: 80
            },{
                id: 'unpluggable',
                dataIndex: 'unpluggable',
                header: _t('Unpluggable'),
                renderer: Zenoss.render.checkbox,
                width: 80
            },{
                id: 'currently_attached',
                dataIndex: 'currently_attached',
                header: _t('Attached'),
                renderer: Zenoss.render.checkbox,
                width: 70
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerVBDPanel.superclass.constructor.call(
            this, config);
    }
});

Ext.reg('XenServerVBDPanel', ZC.XenServerVBDPanel);

Zenoss.nav.appendTo('Component', [{
    id: 'component_vbds',
    text: _t('VBDs'),
    xtype: 'XenServerVBDPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'XenServerSR': return true;
            case 'XenServerVDI': return true;
            case 'XenServerVM': return true;
            case 'XenServerVMAppliance': return true;
            default: return false;
        }
    },
    setContext: function(uid) {
        ZC.XenServerVBDPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

ZC.XenServerVDIPanel = Ext.extend(ZC.XenServerComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'XenServerVDI',
            autoExpandColumn: 'name',
            sortInfo: {
                field: 'name',
                direction: 'asc'
            },
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'meta_type'},
                {name: 'status'},
                {name: 'severity'},
                {name: 'sr'},
                {name: 'vdi_type'},
                {name: 'virtual_size'},
                {name: 'is_a_snapshot'},
                {name: 'read_only'},
                {name: 'on_boot'},
                {name: 'sharable'},
                {name: 'vbd_count'},
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid
            },{
                id: 'sr',
                dataIndex: 'sr',
                header: _t('Storage Repository'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                width: 120
            },{
                id: 'vdi_type',
                dataIndex: 'vdi_type',
                header: _t('Type'),
                width: 70
            },{
                id: 'virtual_size',
                dataIndex: 'virtual_size',
                header: _t('Size'),
                renderer: Zenoss.render.bytesString,
                width: 80
            },{
                id: 'on_boot',
                dataIndex: 'on_boot',
                header: _t('On Boot'),
                width: 70
            },{
                id: 'is_a_snapshot',
                dataIndex: 'is_a_snapshot',
                header: _t('Snapshot'),
                renderer: Zenoss.render.checkbox,
                width: 70
            },{
                id: 'read_only',
                dataIndex: 'read_only',
                header: _t('Read Only'),
                renderer: Zenoss.render.checkbox,
                width: 75
            },{
                id: 'sharable',
                dataIndex: 'sharable',
                header: _t('Sharable'),
                renderer: Zenoss.render.checkbox,
                width: 65
            },{
                id: 'vbd_count',
                dataIndex: 'vbd_count',
                header: _t('VBDs'),
                width: 50
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerVDIPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('XenServerVDIPanel', ZC.XenServerVDIPanel);

Zenoss.nav.appendTo('Component', [{
    id: 'component_vdis',
    text: _t('VDIs'),
    xtype: 'XenServerVDIPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        return navpanel.refOwner.componentType == 'XenServerSR';
    },
    setContext: function(uid) {
        ZC.XenServerVDIPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

ZC.XenServerVIFPanel = Ext.extend(ZC.XenServerComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'XenServerVIF',
            autoExpandColumn: 'network',
            sortInfo: {
                field: 'name',
                direction: 'asc'
            },
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'meta_type'},
                {name: 'status'},
                {name: 'severity'},
                {name: 'vm'},
                {name: 'network'},
                {name: 'locking_mode'},
                {name: 'currently_attached'},
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                width: 100
            },{
                id: 'vm',
                dataIndex: 'vm',
                header: _t('VM'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                width: 120
            },{
                id: 'network',
                dataIndex: 'network',
                header: _t('Network'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid
            },{
                id: 'locking_mode',
                dataIndex: 'locking_mode',
                header: _t('Locking Mode'),
                width: 100
            },{
                id: 'currently_attached',
                dataIndex: 'currently_attached',
                header: _t('Attached'),
                renderer: Zenoss.render.checkbox,
                width: 70
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerVIFPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('XenServerVIFPanel', ZC.XenServerVIFPanel);

Zenoss.nav.appendTo('Component', [{
    id: 'component_vifs',
    text: _t('VIFs'),
    xtype: 'XenServerVIFPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'XenServerNetwork': return true;
            case 'XenServerVM': return true;
            case 'XenServerVMAppliance': return true;
            default: return false;
        }
    },
    setContext: function(uid) {
        ZC.XenServerVIFPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

ZC.XenServerVMPanel = Ext.extend(ZC.XenServerComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'XenServerVM',
            autoExpandColumn: 'name',
            sortInfo: {
                field: 'name',
                direction: 'asc'
            },
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'meta_type'},
                {name: 'status'},
                {name: 'severity'},
                {name: 'host'},
                {name: 'vmappliance'},
                {name: 'vcpus_at_startup'},  // for combined_cpu
                {name: 'vcpus_max'}, // for combined_cpu
                {name: 'memory_actual'},
                {name: 'power_state'},
                {name: 'vbd_count'},
                {name: 'vif_count'},
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid
            },{
                id: 'host',
                dataIndex: 'host',
                header: _t('Host'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                width: 120
            },{
                id: 'vmappliance',
                dataIndex: 'vmappliance',
                header: _t('vApp'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                width: 120
            },{
                id: 'combined_cpu',
                dataIndex: 'vcpus_at_startup',
                header: _t('vCPUs'),
                renderer: function(value, metaData, record) {
                    return '<span title="Startup / Maximum">' +
                        record.data.vcpus_at_startup + ' / ' +
                        record.data.vcpus_max +
                        '</span>';
                },
                width: 60
            },{
                id: 'memory_actual',
                dataIndex: 'memory_actual',
                header: _t('Memory'),
                renderer: Zenoss.render.memory,
                width: 80
            },{
                id: 'power_state',
                dataIndex: 'power_state',
                header: _t('Power State'),
                width: 85
            },{
                id: 'vbd_count',
                dataIndex: 'vbd_count',
                header: _t('VBDs'),
                width: 50
            },{
                id: 'vif_count',
                dataIndex: 'vif_count',
                header: _t('VIFs'),
                width: 50
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerVMPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('XenServerVMPanel', ZC.XenServerVMPanel);

Zenoss.nav.appendTo('Component', [{
    id: 'component_vms',
    text: _t('VMs'),
    xtype: 'XenServerVMPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'XenServerHost': return true;
            case 'XenServerVMAppliance': return true;
            default: return false;
        }
    },
    setContext: function(uid) {
        ZC.XenServerVMPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

ZC.XenServerVMAppliancePanel = Ext.extend(ZC.XenServerComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'XenServerVMAppliance',
            autoExpandColumn: 'name_description',
            sortInfo: {
                field: 'name',
                direction: 'asc'
            },
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'meta_type'},
                {name: 'status'},
                {name: 'severity'},
                {name: 'name_description'},
                {name: 'vm_count'},
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                width: 200
            },{
                id: 'name_description',
                dataIndex: 'name_description',
                header: _t('Description')
            },{
                id: 'vm_count',
                dataIndex: 'vm_count',
                header: _t('VMs'),
                width: 50
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerVMAppliancePanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('XenServerVMAppliancePanel', ZC.XenServerVMAppliancePanel);

})();
