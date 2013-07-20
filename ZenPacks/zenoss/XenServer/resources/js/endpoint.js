(function(){

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
                {name: 'master_for'},
                {name: 'suspend_image_sr'},
                {name: 'crash_dump_sr'},
                {name: 'local_cache_sr'},
                {name: 'hostcpu_count'},
                {name: 'pbd_count'},
                {name: 'pif_count'},
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
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                sortable: true
            },{
                id: 'master_for',
                dataIndex: 'master_for',
                header: _t('Master For'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                width: 120
            },{
                id: 'suspend_image_sr',
                dataIndex: 'suspend_image_sr',
                header: _t('Suspend SR'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                width: 120
            },{
                id: 'crash_dump_sr',
                dataIndex: 'crash_dump_sr',
                header: _t('Crash SR'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                width: 120
            },{
                id: 'local_cache_sr',
                dataIndex: 'local_cache_sr',
                header: _t('Cache SR'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                width: 120
            },{
                id: 'hostcpu_count',
                dataIndex: 'hostcpu_count',
                header: _t('CPUs'),
                width: 60
            },{
                id: 'pbd_count',
                dataIndex: 'pbd_count',
                header: _t('PBDs'),
                width: 60
            },{
                id: 'pif_count',
                dataIndex: 'pif_count',
                header: _t('PIFs'),
                width: 60
            },{
                id: 'vm_count',
                dataIndex: 'vm_count',
                header: _t('VMs'),
                width: 60
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
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
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'family'},
                {name: 'features'},
                {name: 'flags'},
                {name: 'host'},
                {name: 'model'},
                {name: 'modelname'},
                {name: 'number'},
                {name: 'speed'},
                {name: 'stepping'},
                {name: 'utilisation'},
                {name: 'uuid'},
                {name: 'vendor'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'family',
                header: _t('family'),
                sortable: true,
                width: 80,
                id: 'family'
            },{
                dataIndex: 'features',
                header: _t('features'),
                sortable: true,
                width: 80,
                id: 'features'
            },{
                dataIndex: 'flags',
                header: _t('flags'),
                sortable: true,
                width: 80,
                id: 'flags'
            },{
                dataIndex: 'host',
                header: _t('host'),
                sortable: true,
                width: 80,
                id: 'host'
            },{
                dataIndex: 'model',
                header: _t('model'),
                sortable: true,
                width: 80,
                id: 'model'
            },{
                dataIndex: 'modelname',
                header: _t('modelname'),
                sortable: true,
                width: 80,
                id: 'modelname'
            },{
                dataIndex: 'number',
                header: _t('number'),
                sortable: true,
                width: 80,
                id: 'number'
            },{
                dataIndex: 'speed',
                header: _t('speed'),
                sortable: true,
                width: 80,
                id: 'speed'
            },{
                dataIndex: 'stepping',
                header: _t('stepping'),
                sortable: true,
                width: 80,
                id: 'stepping'
            },{
                dataIndex: 'utilisation',
                header: _t('utilisation'),
                sortable: true,
                width: 80,
                id: 'utilisation'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 80,
                id: 'uuid'
            },{
                dataIndex: 'vendor',
                header: _t('vendor'),
                sortable: true,
                width: 80,
                id: 'vendor'
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerHostCPUPanel.superclass.constructor.call(
            this, config);
    }
});

Ext.reg('XenServerHostCPUPanel', ZC.XenServerHostCPUPanel);

ZC.XenServerHostCPUPanel = Ext.extend(ZC.XenServerComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'XenServerHostCPU',
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
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'family'},
                {name: 'features'},
                {name: 'flags'},
                {name: 'host'},
                {name: 'model'},
                {name: 'modelname'},
                {name: 'number'},
                {name: 'speed'},
                {name: 'stepping'},
                {name: 'utilisation'},
                {name: 'uuid'},
                {name: 'vendor'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'family',
                header: _t('family'),
                sortable: true,
                width: 80,
                id: 'family'
            },{
                dataIndex: 'features',
                header: _t('features'),
                sortable: true,
                width: 80,
                id: 'features'
            },{
                dataIndex: 'flags',
                header: _t('flags'),
                sortable: true,
                width: 80,
                id: 'flags'
            },{
                dataIndex: 'host',
                header: _t('host'),
                sortable: true,
                width: 80,
                id: 'host'
            },{
                dataIndex: 'model',
                header: _t('model'),
                sortable: true,
                width: 80,
                id: 'model'
            },{
                dataIndex: 'modelname',
                header: _t('modelname'),
                sortable: true,
                width: 80,
                id: 'modelname'
            },{
                dataIndex: 'number',
                header: _t('number'),
                sortable: true,
                width: 80,
                id: 'number'
            },{
                dataIndex: 'speed',
                header: _t('speed'),
                sortable: true,
                width: 80,
                id: 'speed'
            },{
                dataIndex: 'stepping',
                header: _t('stepping'),
                sortable: true,
                width: 80,
                id: 'stepping'
            },{
                dataIndex: 'utilisation',
                header: _t('utilisation'),
                sortable: true,
                width: 80,
                id: 'utilisation'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 80,
                id: 'uuid'
            },{
                dataIndex: 'vendor',
                header: _t('vendor'),
                sortable: true,
                width: 80,
                id: 'vendor'
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerHostCPUPanel.superclass.constructor.call(
            this, config);
    }
});

Ext.reg('XenServerHostCPUPanel', ZC.XenServerHostCPUPanel);

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
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'bridge'},
                {name: 'default_locking_mode'},
                {name: 'MTU'},
                {name: 'name_description'},
                {name: 'name_label'},
                {name: 'tags'},
                {name: 'uuid'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'bridge',
                header: _t('bridge'),
                sortable: true,
                width: 80,
                id: 'bridge'
            },{
                dataIndex: 'default_locking_mode',
                header: _t('default_locking_mode'),
                sortable: true,
                width: 80,
                id: 'default_locking_mode'
            },{
                dataIndex: 'MTU',
                header: _t('MTU'),
                sortable: true,
                width: 80,
                id: 'MTU'
            },{
                dataIndex: 'name_description',
                header: _t('name_description'),
                sortable: true,
                width: 80,
                id: 'name_description'
            },{
                dataIndex: 'name_label',
                header: _t('name_label'),
                sortable: true,
                width: 80,
                id: 'name_label'
            },{
                dataIndex: 'tags',
                header: _t('tags'),
                sortable: true,
                width: 80,
                id: 'tags'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 80,
                id: 'uuid'
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerNetworkPanel.superclass.constructor.call(
            this, config);
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
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'current_attached'},
                {name: 'dc_legacy_mode'},
                {name: 'dc_location'},
                {name: 'dc_device'},
                {name: 'uuid'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'current_attached',
                header: _t('current_attached'),
                sortable: true,
                width: 80,
                id: 'current_attached'
            },{
                dataIndex: 'dc_legacy_mode',
                header: _t('dc_legacy_mode'),
                sortable: true,
                width: 80,
                id: 'dc_legacy_mode'
            },{
                dataIndex: 'dc_location',
                header: _t('dc_location'),
                sortable: true,
                width: 80,
                id: 'dc_location'
            },{
                dataIndex: 'dc_device',
                header: _t('dc_device'),
                sortable: true,
                width: 80,
                id: 'dc_device'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 80,
                id: 'uuid'
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerPBDPanel.superclass.constructor.call(
            this, config);
    }
});

Ext.reg('XenServerPBDPanel', ZC.XenServerPBDPanel);

Zenoss.nav.appendTo('Component', [{
    id: 'component_pbds',
    text: _t('PBDS'),
    xtype: 'XenServerPBDPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'XenServerSR': return true;
            default: return false;
        }
    },
    setContext: function(uid) {
        ZC.XenServerPBDPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

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
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'current_attached'},
                {name: 'dc_legacy_mode'},
                {name: 'dc_location'},
                {name: 'dc_device'},
                {name: 'uuid'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'current_attached',
                header: _t('current_attached'),
                sortable: true,
                width: 80,
                id: 'current_attached'
            },{
                dataIndex: 'dc_legacy_mode',
                header: _t('dc_legacy_mode'),
                sortable: true,
                width: 80,
                id: 'dc_legacy_mode'
            },{
                dataIndex: 'dc_location',
                header: _t('dc_location'),
                sortable: true,
                width: 80,
                id: 'dc_location'
            },{
                dataIndex: 'dc_device',
                header: _t('dc_device'),
                sortable: true,
                width: 80,
                id: 'dc_device'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 80,
                id: 'uuid'
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerPBDPanel.superclass.constructor.call(
            this, config);
    }
});

Ext.reg('XenServerPBDPanel', ZC.XenServerPBDPanel);

Zenoss.nav.appendTo('Component', [{
    id: 'component_pbds',
    text: _t('PBDS'),
    xtype: 'XenServerPBDPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'XenServerSR': return true;
            default: return false;
        }
    },
    setContext: function(uid) {
        ZC.XenServerPBDPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

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
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'current_attached'},
                {name: 'dc_legacy_mode'},
                {name: 'dc_location'},
                {name: 'dc_device'},
                {name: 'uuid'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'current_attached',
                header: _t('current_attached'),
                sortable: true,
                width: 80,
                id: 'current_attached'
            },{
                dataIndex: 'dc_legacy_mode',
                header: _t('dc_legacy_mode'),
                sortable: true,
                width: 80,
                id: 'dc_legacy_mode'
            },{
                dataIndex: 'dc_location',
                header: _t('dc_location'),
                sortable: true,
                width: 80,
                id: 'dc_location'
            },{
                dataIndex: 'dc_device',
                header: _t('dc_device'),
                sortable: true,
                width: 80,
                id: 'dc_device'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 80,
                id: 'uuid'
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerPBDPanel.superclass.constructor.call(
            this, config);
    }
});

Ext.reg('XenServerPBDPanel', ZC.XenServerPBDPanel);

Zenoss.nav.appendTo('Component', [{
    id: 'component_pbds',
    text: _t('PBDS'),
    xtype: 'XenServerPBDPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
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
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'gateway'},
                {name: 'IP'},
                {name: 'MAC'},
                {name: 'netmask'},
                {name: 'uuid'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'gateway',
                header: _t('gateway'),
                sortable: true,
                width: 80,
                id: 'gateway'
            },{
                dataIndex: 'IP',
                header: _t('IP'),
                sortable: true,
                width: 80,
                id: 'IP'
            },{
                dataIndex: 'MAC',
                header: _t('MAC'),
                sortable: true,
                width: 80,
                id: 'MAC'
            },{
                dataIndex: 'netmask',
                header: _t('netmask'),
                sortable: true,
                width: 80,
                id: 'netmask'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 80,
                id: 'uuid'
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerPIFPanel.superclass.constructor.call(
            this, config);
    }
});

Ext.reg('XenServerPIFPanel', ZC.XenServerPIFPanel);

Zenoss.nav.appendTo('Component', [{
    id: 'component_pifs',
    text: _t('PIFS'),
    xtype: 'XenServerPIFPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'XenServerNetwork': return true;
            default: return false;
        }
    },
    setContext: function(uid) {
        ZC.XenServerPIFPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

ZC.XenServerPIFPanel = Ext.extend(ZC.XenServerComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'XenServerPIF',
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
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'gateway'},
                {name: 'IP'},
                {name: 'MAC'},
                {name: 'netmask'},
                {name: 'uuid'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'gateway',
                header: _t('gateway'),
                sortable: true,
                width: 80,
                id: 'gateway'
            },{
                dataIndex: 'IP',
                header: _t('IP'),
                sortable: true,
                width: 80,
                id: 'IP'
            },{
                dataIndex: 'MAC',
                header: _t('MAC'),
                sortable: true,
                width: 80,
                id: 'MAC'
            },{
                dataIndex: 'netmask',
                header: _t('netmask'),
                sortable: true,
                width: 80,
                id: 'netmask'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 80,
                id: 'uuid'
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerPIFPanel.superclass.constructor.call(
            this, config);
    }
});

Ext.reg('XenServerPIFPanel', ZC.XenServerPIFPanel);

Zenoss.nav.appendTo('Component', [{
    id: 'component_pifs',
    text: _t('PIFS'),
    xtype: 'XenServerPIFPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'XenServerNetwork': return true;
            default: return false;
        }
    },
    setContext: function(uid) {
        ZC.XenServerPIFPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

ZC.XenServerPIFPanel = Ext.extend(ZC.XenServerComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'XenServerPIF',
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
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'gateway'},
                {name: 'IP'},
                {name: 'MAC'},
                {name: 'netmask'},
                {name: 'uuid'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'gateway',
                header: _t('gateway'),
                sortable: true,
                width: 80,
                id: 'gateway'
            },{
                dataIndex: 'IP',
                header: _t('IP'),
                sortable: true,
                width: 80,
                id: 'IP'
            },{
                dataIndex: 'MAC',
                header: _t('MAC'),
                sortable: true,
                width: 80,
                id: 'MAC'
            },{
                dataIndex: 'netmask',
                header: _t('netmask'),
                sortable: true,
                width: 80,
                id: 'netmask'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 80,
                id: 'uuid'
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerPIFPanel.superclass.constructor.call(
            this, config);
    }
});

Ext.reg('XenServerPIFPanel', ZC.XenServerPIFPanel);

Zenoss.nav.appendTo('Component', [{
    id: 'component_pifs',
    text: _t('PIFS'),
    xtype: 'XenServerPIFPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
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
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'ha_allow_overcommit'},
                {name: 'ha_enabled'},
                {name: 'ha_host_failures_to_tolerate'},
                {name: 'ha_overcommitted'},
                {name: 'ha_plan_exists_for'},
                {name: 'name_description'},
                {name: 'name_label'},
                {name: 'redo_log_enabled'},
                {name: 'uuid'},
                {name: 'vswitch_controller'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'ha_allow_overcommit',
                header: _t('ha_allow_overcommit'),
                sortable: true,
                width: 80,
                id: 'ha_allow_overcommit'
            },{
                dataIndex: 'ha_enabled',
                header: _t('ha_enabled'),
                sortable: true,
                width: 80,
                id: 'ha_enabled'
            },{
                dataIndex: 'ha_host_failures_to_tolerate',
                header: _t('ha_host_failures_to_tolerate'),
                sortable: true,
                width: 80,
                id: 'ha_host_failures_to_tolerate'
            },{
                dataIndex: 'ha_overcommitted',
                header: _t('ha_overcommitted'),
                sortable: true,
                width: 80,
                id: 'ha_overcommitted'
            },{
                dataIndex: 'ha_plan_exists_for',
                header: _t('ha_plan_exists_for'),
                sortable: true,
                width: 80,
                id: 'ha_plan_exists_for'
            },{
                dataIndex: 'name_description',
                header: _t('name_description'),
                sortable: true,
                width: 80,
                id: 'name_description'
            },{
                dataIndex: 'name_label',
                header: _t('name_label'),
                sortable: true,
                width: 80,
                id: 'name_label'
            },{
                dataIndex: 'redo_log_enabled',
                header: _t('redo_log_enabled'),
                sortable: true,
                width: 80,
                id: 'redo_log_enabled'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 80,
                id: 'uuid'
            },{
                dataIndex: 'vswitch_controller',
                header: _t('vswitch_controller'),
                sortable: true,
                width: 80,
                id: 'vswitch_controller'
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerPoolPanel.superclass.constructor.call(
            this, config);
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
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'name_description'},
                {name: 'name_label'},
                {name: 'content_type'},
                {name: 'physical_size'},
                {name: 'physical_utilisation'},
                {name: 'shared'},
                {name: 'virtual_allocation'},
                {name: 'uuid'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'name_description',
                header: _t('name_description'),
                sortable: true,
                width: 80,
                id: 'name_description'
            },{
                dataIndex: 'name_label',
                header: _t('name_label'),
                sortable: true,
                width: 80,
                id: 'name_label'
            },{
                dataIndex: 'content_type',
                header: _t('content_type'),
                sortable: true,
                width: 80,
                id: 'content_type'
            },{
                dataIndex: 'physical_size',
                header: _t('physical_size'),
                sortable: true,
                width: 80,
                id: 'physical_size'
            },{
                dataIndex: 'physical_utilisation',
                header: _t('physical_utilisation'),
                sortable: true,
                width: 80,
                id: 'physical_utilisation'
            },{
                dataIndex: 'shared',
                header: _t('shared'),
                sortable: true,
                width: 80,
                id: 'shared'
            },{
                dataIndex: 'virtual_allocation',
                header: _t('virtual_allocation'),
                sortable: true,
                width: 80,
                id: 'virtual_allocation'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 80,
                id: 'uuid'
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerSRPanel.superclass.constructor.call(
            this, config);
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
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'bootable'},
                {name: 'current_attached'},
                {name: 'empty'},
                {name: 'status_code'},
                {name: 'status_detail'},
                {name: 'Type'},
                {name: 'uuid'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'bootable',
                header: _t('bootable'),
                sortable: true,
                width: 80,
                id: 'bootable'
            },{
                dataIndex: 'current_attached',
                header: _t('current_attached'),
                sortable: true,
                width: 80,
                id: 'current_attached'
            },{
                dataIndex: 'empty',
                header: _t('empty'),
                sortable: true,
                width: 80,
                id: 'empty'
            },{
                dataIndex: 'status_code',
                header: _t('status_code'),
                sortable: true,
                width: 80,
                id: 'status_code'
            },{
                dataIndex: 'status_detail',
                header: _t('status_detail'),
                sortable: true,
                width: 80,
                id: 'status_detail'
            },{
                dataIndex: 'Type',
                header: _t('Type'),
                sortable: true,
                width: 80,
                id: 'Type'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 80,
                id: 'uuid'
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
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
    text: _t('VBDS'),
    xtype: 'XenServerVBDPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'XenServerVDI': return true;
            default: return false;
        }
    },
    setContext: function(uid) {
        ZC.XenServerVBDPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

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
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'bootable'},
                {name: 'current_attached'},
                {name: 'empty'},
                {name: 'status_code'},
                {name: 'status_detail'},
                {name: 'Type'},
                {name: 'uuid'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'bootable',
                header: _t('bootable'),
                sortable: true,
                width: 80,
                id: 'bootable'
            },{
                dataIndex: 'current_attached',
                header: _t('current_attached'),
                sortable: true,
                width: 80,
                id: 'current_attached'
            },{
                dataIndex: 'empty',
                header: _t('empty'),
                sortable: true,
                width: 80,
                id: 'empty'
            },{
                dataIndex: 'status_code',
                header: _t('status_code'),
                sortable: true,
                width: 80,
                id: 'status_code'
            },{
                dataIndex: 'status_detail',
                header: _t('status_detail'),
                sortable: true,
                width: 80,
                id: 'status_detail'
            },{
                dataIndex: 'Type',
                header: _t('Type'),
                sortable: true,
                width: 80,
                id: 'Type'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 80,
                id: 'uuid'
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
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
    text: _t('VBDS'),
    xtype: 'XenServerVBDPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'XenServerVDI': return true;
            default: return false;
        }
    },
    setContext: function(uid) {
        ZC.XenServerVBDPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

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
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'bootable'},
                {name: 'current_attached'},
                {name: 'empty'},
                {name: 'status_code'},
                {name: 'status_detail'},
                {name: 'Type'},
                {name: 'uuid'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'bootable',
                header: _t('bootable'),
                sortable: true,
                width: 80,
                id: 'bootable'
            },{
                dataIndex: 'current_attached',
                header: _t('current_attached'),
                sortable: true,
                width: 80,
                id: 'current_attached'
            },{
                dataIndex: 'empty',
                header: _t('empty'),
                sortable: true,
                width: 80,
                id: 'empty'
            },{
                dataIndex: 'status_code',
                header: _t('status_code'),
                sortable: true,
                width: 80,
                id: 'status_code'
            },{
                dataIndex: 'status_detail',
                header: _t('status_detail'),
                sortable: true,
                width: 80,
                id: 'status_detail'
            },{
                dataIndex: 'Type',
                header: _t('Type'),
                sortable: true,
                width: 80,
                id: 'Type'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 80,
                id: 'uuid'
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
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
    text: _t('VBDS'),
    xtype: 'XenServerVBDPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'XenServerVDI': return true;
            default: return false;
        }
    },
    setContext: function(uid) {
        ZC.XenServerVBDPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

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
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'bootable'},
                {name: 'current_attached'},
                {name: 'empty'},
                {name: 'status_code'},
                {name: 'status_detail'},
                {name: 'Type'},
                {name: 'uuid'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'bootable',
                header: _t('bootable'),
                sortable: true,
                width: 80,
                id: 'bootable'
            },{
                dataIndex: 'current_attached',
                header: _t('current_attached'),
                sortable: true,
                width: 80,
                id: 'current_attached'
            },{
                dataIndex: 'empty',
                header: _t('empty'),
                sortable: true,
                width: 80,
                id: 'empty'
            },{
                dataIndex: 'status_code',
                header: _t('status_code'),
                sortable: true,
                width: 80,
                id: 'status_code'
            },{
                dataIndex: 'status_detail',
                header: _t('status_detail'),
                sortable: true,
                width: 80,
                id: 'status_detail'
            },{
                dataIndex: 'Type',
                header: _t('Type'),
                sortable: true,
                width: 80,
                id: 'Type'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 80,
                id: 'uuid'
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
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
    text: _t('VBDS'),
    xtype: 'XenServerVBDPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'XenServerVDI': return true;
            default: return false;
        }
    },
    setContext: function(uid) {
        ZC.XenServerVBDPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

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
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'bootable'},
                {name: 'current_attached'},
                {name: 'empty'},
                {name: 'status_code'},
                {name: 'status_detail'},
                {name: 'Type'},
                {name: 'uuid'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'bootable',
                header: _t('bootable'),
                sortable: true,
                width: 80,
                id: 'bootable'
            },{
                dataIndex: 'current_attached',
                header: _t('current_attached'),
                sortable: true,
                width: 80,
                id: 'current_attached'
            },{
                dataIndex: 'empty',
                header: _t('empty'),
                sortable: true,
                width: 80,
                id: 'empty'
            },{
                dataIndex: 'status_code',
                header: _t('status_code'),
                sortable: true,
                width: 80,
                id: 'status_code'
            },{
                dataIndex: 'status_detail',
                header: _t('status_detail'),
                sortable: true,
                width: 80,
                id: 'status_detail'
            },{
                dataIndex: 'Type',
                header: _t('Type'),
                sortable: true,
                width: 80,
                id: 'Type'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 80,
                id: 'uuid'
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
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
    text: _t('VBDS'),
    xtype: 'XenServerVBDPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'XenServerVDI': return true;
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
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'allow_caching'},
                {name: 'missing'},
                {name: 'name_description'},
                {name: 'name_label'},
                {name: 'on_boot'},
                {name: 'physical_utilisation'},
                {name: 'read_only'},
                {name: 'sharable'},
                {name: 'Type'},
                {name: 'virtual_size'},
                {name: 'uuid'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'allow_caching',
                header: _t('allow_caching'),
                sortable: true,
                width: 80,
                id: 'allow_caching'
            },{
                dataIndex: 'missing',
                header: _t('missing'),
                sortable: true,
                width: 80,
                id: 'missing'
            },{
                dataIndex: 'name_description',
                header: _t('name_description'),
                sortable: true,
                width: 80,
                id: 'name_description'
            },{
                dataIndex: 'name_label',
                header: _t('name_label'),
                sortable: true,
                width: 80,
                id: 'name_label'
            },{
                dataIndex: 'on_boot',
                header: _t('on_boot'),
                sortable: true,
                width: 80,
                id: 'on_boot'
            },{
                dataIndex: 'physical_utilisation',
                header: _t('physical_utilisation'),
                sortable: true,
                width: 80,
                id: 'physical_utilisation'
            },{
                dataIndex: 'read_only',
                header: _t('read_only'),
                sortable: true,
                width: 80,
                id: 'read_only'
            },{
                dataIndex: 'sharable',
                header: _t('sharable'),
                sortable: true,
                width: 80,
                id: 'sharable'
            },{
                dataIndex: 'Type',
                header: _t('Type'),
                sortable: true,
                width: 80,
                id: 'Type'
            },{
                dataIndex: 'virtual_size',
                header: _t('virtual_size'),
                sortable: true,
                width: 80,
                id: 'virtual_size'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 80,
                id: 'uuid'
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerVDIPanel.superclass.constructor.call(
            this, config);
    }
});

Ext.reg('XenServerVDIPanel', ZC.XenServerVDIPanel);

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
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'allow_caching'},
                {name: 'missing'},
                {name: 'name_description'},
                {name: 'name_label'},
                {name: 'on_boot'},
                {name: 'physical_utilisation'},
                {name: 'read_only'},
                {name: 'sharable'},
                {name: 'Type'},
                {name: 'virtual_size'},
                {name: 'uuid'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'allow_caching',
                header: _t('allow_caching'),
                sortable: true,
                width: 80,
                id: 'allow_caching'
            },{
                dataIndex: 'missing',
                header: _t('missing'),
                sortable: true,
                width: 80,
                id: 'missing'
            },{
                dataIndex: 'name_description',
                header: _t('name_description'),
                sortable: true,
                width: 80,
                id: 'name_description'
            },{
                dataIndex: 'name_label',
                header: _t('name_label'),
                sortable: true,
                width: 80,
                id: 'name_label'
            },{
                dataIndex: 'on_boot',
                header: _t('on_boot'),
                sortable: true,
                width: 80,
                id: 'on_boot'
            },{
                dataIndex: 'physical_utilisation',
                header: _t('physical_utilisation'),
                sortable: true,
                width: 80,
                id: 'physical_utilisation'
            },{
                dataIndex: 'read_only',
                header: _t('read_only'),
                sortable: true,
                width: 80,
                id: 'read_only'
            },{
                dataIndex: 'sharable',
                header: _t('sharable'),
                sortable: true,
                width: 80,
                id: 'sharable'
            },{
                dataIndex: 'Type',
                header: _t('Type'),
                sortable: true,
                width: 80,
                id: 'Type'
            },{
                dataIndex: 'virtual_size',
                header: _t('virtual_size'),
                sortable: true,
                width: 80,
                id: 'virtual_size'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 80,
                id: 'uuid'
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerVDIPanel.superclass.constructor.call(
            this, config);
    }
});

Ext.reg('XenServerVDIPanel', ZC.XenServerVDIPanel);

ZC.XenServerVIFPanel = Ext.extend(ZC.XenServerComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'XenServerVIF',
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
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'MAC'},
                {name: 'MTU'},
                {name: 'qos_algorithm_type'},
                {name: 'status_code'},
                {name: 'status_detail'},
                {name: 'uuid'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'MAC',
                header: _t('MAC'),
                sortable: true,
                width: 80,
                id: 'MAC'
            },{
                dataIndex: 'MTU',
                header: _t('MTU'),
                sortable: true,
                width: 80,
                id: 'MTU'
            },{
                dataIndex: 'qos_algorithm_type',
                header: _t('qos_algorithm_type'),
                sortable: true,
                width: 80,
                id: 'qos_algorithm_type'
            },{
                dataIndex: 'status_code',
                header: _t('status_code'),
                sortable: true,
                width: 80,
                id: 'status_code'
            },{
                dataIndex: 'status_detail',
                header: _t('status_detail'),
                sortable: true,
                width: 80,
                id: 'status_detail'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 80,
                id: 'uuid'
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerVIFPanel.superclass.constructor.call(
            this, config);
    }
});

Ext.reg('XenServerVIFPanel', ZC.XenServerVIFPanel);

Zenoss.nav.appendTo('Component', [{
    id: 'component_vifs',
    text: _t('VIFS'),
    xtype: 'XenServerVIFPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'XenServerNetwork': return true;
            default: return false;
        }
    },
    setContext: function(uid) {
        ZC.XenServerVIFPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

ZC.XenServerVIFPanel = Ext.extend(ZC.XenServerComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'XenServerVIF',
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
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'MAC'},
                {name: 'MTU'},
                {name: 'qos_algorithm_type'},
                {name: 'status_code'},
                {name: 'status_detail'},
                {name: 'uuid'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'MAC',
                header: _t('MAC'),
                sortable: true,
                width: 80,
                id: 'MAC'
            },{
                dataIndex: 'MTU',
                header: _t('MTU'),
                sortable: true,
                width: 80,
                id: 'MTU'
            },{
                dataIndex: 'qos_algorithm_type',
                header: _t('qos_algorithm_type'),
                sortable: true,
                width: 80,
                id: 'qos_algorithm_type'
            },{
                dataIndex: 'status_code',
                header: _t('status_code'),
                sortable: true,
                width: 80,
                id: 'status_code'
            },{
                dataIndex: 'status_detail',
                header: _t('status_detail'),
                sortable: true,
                width: 80,
                id: 'status_detail'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 80,
                id: 'uuid'
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerVIFPanel.superclass.constructor.call(
            this, config);
    }
});

Ext.reg('XenServerVIFPanel', ZC.XenServerVIFPanel);

Zenoss.nav.appendTo('Component', [{
    id: 'component_vifs',
    text: _t('VIFS'),
    xtype: 'XenServerVIFPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'XenServerNetwork': return true;
            default: return false;
        }
    },
    setContext: function(uid) {
        ZC.XenServerVIFPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

ZC.XenServerVIFPanel = Ext.extend(ZC.XenServerComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'XenServerVIF',
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
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'MAC'},
                {name: 'MTU'},
                {name: 'qos_algorithm_type'},
                {name: 'status_code'},
                {name: 'status_detail'},
                {name: 'uuid'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'MAC',
                header: _t('MAC'),
                sortable: true,
                width: 80,
                id: 'MAC'
            },{
                dataIndex: 'MTU',
                header: _t('MTU'),
                sortable: true,
                width: 80,
                id: 'MTU'
            },{
                dataIndex: 'qos_algorithm_type',
                header: _t('qos_algorithm_type'),
                sortable: true,
                width: 80,
                id: 'qos_algorithm_type'
            },{
                dataIndex: 'status_code',
                header: _t('status_code'),
                sortable: true,
                width: 80,
                id: 'status_code'
            },{
                dataIndex: 'status_detail',
                header: _t('status_detail'),
                sortable: true,
                width: 80,
                id: 'status_detail'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 80,
                id: 'uuid'
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerVIFPanel.superclass.constructor.call(
            this, config);
    }
});

Ext.reg('XenServerVIFPanel', ZC.XenServerVIFPanel);

Zenoss.nav.appendTo('Component', [{
    id: 'component_vifs',
    text: _t('VIFS'),
    xtype: 'XenServerVIFPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'XenServerNetwork': return true;
            default: return false;
        }
    },
    setContext: function(uid) {
        ZC.XenServerVIFPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

ZC.XenServerVIFPanel = Ext.extend(ZC.XenServerComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'XenServerVIF',
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
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'MAC'},
                {name: 'MTU'},
                {name: 'qos_algorithm_type'},
                {name: 'status_code'},
                {name: 'status_detail'},
                {name: 'uuid'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'MAC',
                header: _t('MAC'),
                sortable: true,
                width: 80,
                id: 'MAC'
            },{
                dataIndex: 'MTU',
                header: _t('MTU'),
                sortable: true,
                width: 80,
                id: 'MTU'
            },{
                dataIndex: 'qos_algorithm_type',
                header: _t('qos_algorithm_type'),
                sortable: true,
                width: 80,
                id: 'qos_algorithm_type'
            },{
                dataIndex: 'status_code',
                header: _t('status_code'),
                sortable: true,
                width: 80,
                id: 'status_code'
            },{
                dataIndex: 'status_detail',
                header: _t('status_detail'),
                sortable: true,
                width: 80,
                id: 'status_detail'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 80,
                id: 'uuid'
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerVIFPanel.superclass.constructor.call(
            this, config);
    }
});

Ext.reg('XenServerVIFPanel', ZC.XenServerVIFPanel);

Zenoss.nav.appendTo('Component', [{
    id: 'component_vifs',
    text: _t('VIFS'),
    xtype: 'XenServerVIFPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'XenServerNetwork': return true;
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
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'VCPUs_max'},
                {name: 'VCPUs_at_startup'},
                {name: 'memory_dynamic_max'},
                {name: 'memory_dynamic_min'},
                {name: 'memory_overhead'},
                {name: 'memory_static_max'},
                {name: 'memory_static_min'},
                {name: 'name_label'},
                {name: 'name_description'},
                {name: 'power_state'},
                {name: 'uuid'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'VCPUs_max',
                header: _t('VCPUs_max'),
                sortable: true,
                width: 80,
                id: 'VCPUs_max'
            },{
                dataIndex: 'VCPUs_at_startup',
                header: _t('VCPUs_at_startup'),
                sortable: true,
                width: 80,
                id: 'VCPUs_at_startup'
            },{
                dataIndex: 'memory_dynamic_max',
                header: _t('memory_dynamic_max'),
                sortable: true,
                width: 80,
                id: 'memory_dynamic_max'
            },{
                dataIndex: 'memory_dynamic_min',
                header: _t('memory_dynamic_min'),
                sortable: true,
                width: 80,
                id: 'memory_dynamic_min'
            },{
                dataIndex: 'memory_overhead',
                header: _t('memory_overhead'),
                sortable: true,
                width: 80,
                id: 'memory_overhead'
            },{
                dataIndex: 'memory_static_max',
                header: _t('memory_static_max'),
                sortable: true,
                width: 80,
                id: 'memory_static_max'
            },{
                dataIndex: 'memory_static_min',
                header: _t('memory_static_min'),
                sortable: true,
                width: 80,
                id: 'memory_static_min'
            },{
                dataIndex: 'name_label',
                header: _t('name_label'),
                sortable: true,
                width: 80,
                id: 'name_label'
            },{
                dataIndex: 'name_description',
                header: _t('name_description'),
                sortable: true,
                width: 80,
                id: 'name_description'
            },{
                dataIndex: 'power_state',
                header: _t('power_state'),
                sortable: true,
                width: 80,
                id: 'power_state'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 80,
                id: 'uuid'
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerVMPanel.superclass.constructor.call(
            this, config);
    }
});

Ext.reg('XenServerVMPanel', ZC.XenServerVMPanel);

Zenoss.nav.appendTo('Component', [{
    id: 'component_vms',
    text: _t('VMS'),
    xtype: 'XenServerVMPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'XenServerHost': return true;
            default: return false;
        }
    },
    setContext: function(uid) {
        ZC.XenServerVMPanel.superclass.setContext.apply(this, [uid]);
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
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'VCPUs_max'},
                {name: 'VCPUs_at_startup'},
                {name: 'memory_dynamic_max'},
                {name: 'memory_dynamic_min'},
                {name: 'memory_overhead'},
                {name: 'memory_static_max'},
                {name: 'memory_static_min'},
                {name: 'name_label'},
                {name: 'name_description'},
                {name: 'power_state'},
                {name: 'uuid'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'VCPUs_max',
                header: _t('VCPUs_max'),
                sortable: true,
                width: 80,
                id: 'VCPUs_max'
            },{
                dataIndex: 'VCPUs_at_startup',
                header: _t('VCPUs_at_startup'),
                sortable: true,
                width: 80,
                id: 'VCPUs_at_startup'
            },{
                dataIndex: 'memory_dynamic_max',
                header: _t('memory_dynamic_max'),
                sortable: true,
                width: 80,
                id: 'memory_dynamic_max'
            },{
                dataIndex: 'memory_dynamic_min',
                header: _t('memory_dynamic_min'),
                sortable: true,
                width: 80,
                id: 'memory_dynamic_min'
            },{
                dataIndex: 'memory_overhead',
                header: _t('memory_overhead'),
                sortable: true,
                width: 80,
                id: 'memory_overhead'
            },{
                dataIndex: 'memory_static_max',
                header: _t('memory_static_max'),
                sortable: true,
                width: 80,
                id: 'memory_static_max'
            },{
                dataIndex: 'memory_static_min',
                header: _t('memory_static_min'),
                sortable: true,
                width: 80,
                id: 'memory_static_min'
            },{
                dataIndex: 'name_label',
                header: _t('name_label'),
                sortable: true,
                width: 80,
                id: 'name_label'
            },{
                dataIndex: 'name_description',
                header: _t('name_description'),
                sortable: true,
                width: 80,
                id: 'name_description'
            },{
                dataIndex: 'power_state',
                header: _t('power_state'),
                sortable: true,
                width: 80,
                id: 'power_state'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 80,
                id: 'uuid'
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.XenServerVMPanel.superclass.constructor.call(
            this, config);
    }
});

Ext.reg('XenServerVMPanel', ZC.XenServerVMPanel);

Zenoss.nav.appendTo('Component', [{
    id: 'component_vms',
    text: _t('VMS'),
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
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.xenserver_entityLinkFromGrid,
                sortable: true
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
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
