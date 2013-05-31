(function(){

var ZC = Ext.ns('Zenoss.component');

Ext.apply(Zenoss.render, {
    ZenPacks_zenoss_XenServer__Products_ZenModel_Device_Device_entityLinkFromGrid: function(obj, col, record) {
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
    },
});

ZC.PIFPanel = Ext.extend(ZC.ZenPacks_zenoss_XenServer__Products_ZenModel_Device_DeviceComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'PIF',
            autoExpandColumn: 'name',
            sortInfo: {
                field: 'name',
                direction: 'asc',
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
                renderer: Zenoss.render.NetBotz_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'gateway',
                header: _t('gateway'),
                sortable: true,
                width: 10,
                id: 'gateway'
            },{
                dataIndex: 'IP',
                header: _t('IP'),
                sortable: true,
                width: 10,
                id: 'IP'
            },{
                dataIndex: 'MAC',
                header: _t('MAC'),
                sortable: true,
                width: 10,
                id: 'MAC'
            },{
                dataIndex: 'netmask',
                header: _t('netmask'),
                sortable: true,
                width: 10,
                id: 'netmask'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 10,
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

        ZC.PIFPanel.superclass.constructor.call(
            this, config);
    }
});

Ext.reg('PIFPanel', ZC.PIFPanel);

ZC.SRPanel = Ext.extend(ZC.ZenPacks_zenoss_XenServer__Products_ZenModel_Device_DeviceComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'SR',
            autoExpandColumn: 'name',
            sortInfo: {
                field: 'name',
                direction: 'asc',
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
                renderer: Zenoss.render.NetBotz_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'name_description',
                header: _t('name_description'),
                sortable: true,
                width: 10,
                id: 'name_description'
            },{
                dataIndex: 'name_label',
                header: _t('name_label'),
                sortable: true,
                width: 10,
                id: 'name_label'
            },{
                dataIndex: 'content_type',
                header: _t('content_type'),
                sortable: true,
                width: 10,
                id: 'content_type'
            },{
                dataIndex: 'physical_size',
                header: _t('physical_size'),
                sortable: true,
                width: 10,
                id: 'physical_size'
            },{
                dataIndex: 'physical_utilisation',
                header: _t('physical_utilisation'),
                sortable: true,
                width: 10,
                id: 'physical_utilisation'
            },{
                dataIndex: 'shared',
                header: _t('shared'),
                sortable: true,
                width: 10,
                id: 'shared'
            },{
                dataIndex: 'virtual_allocation',
                header: _t('virtual_allocation'),
                sortable: true,
                width: 10,
                id: 'virtual_allocation'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 10,
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

        ZC.SRPanel.superclass.constructor.call(
            this, config);
    }
});

Ext.reg('SRPanel', ZC.SRPanel);

ZC.VBDPanel = Ext.extend(ZC.ZenPacks_zenoss_XenServer__Products_ZenModel_Device_DeviceComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'VBD',
            autoExpandColumn: 'name',
            sortInfo: {
                field: 'name',
                direction: 'asc',
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
                {name: 'type'},
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
                renderer: Zenoss.render.NetBotz_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'bootable',
                header: _t('bootable'),
                sortable: true,
                width: 10,
                id: 'bootable'
            },{
                dataIndex: 'current_attached',
                header: _t('current_attached'),
                sortable: true,
                width: 10,
                id: 'current_attached'
            },{
                dataIndex: 'empty',
                header: _t('empty'),
                sortable: true,
                width: 10,
                id: 'empty'
            },{
                dataIndex: 'status_code',
                header: _t('status_code'),
                sortable: true,
                width: 10,
                id: 'status_code'
            },{
                dataIndex: 'status_detail',
                header: _t('status_detail'),
                sortable: true,
                width: 10,
                id: 'status_detail'
            },{
                dataIndex: 'type',
                header: _t('type'),
                sortable: true,
                width: 10,
                id: 'type'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 10,
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

        ZC.VBDPanel.superclass.constructor.call(
            this, config);
    }
});

Ext.reg('VBDPanel', ZC.VBDPanel);

ZC.VDIPanel = Ext.extend(ZC.ZenPacks_zenoss_XenServer__Products_ZenModel_Device_DeviceComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'VDI',
            autoExpandColumn: 'name',
            sortInfo: {
                field: 'name',
                direction: 'asc',
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
                {name: 'type'},
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
                renderer: Zenoss.render.NetBotz_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'allow_caching',
                header: _t('allow_caching'),
                sortable: true,
                width: 10,
                id: 'allow_caching'
            },{
                dataIndex: 'missing',
                header: _t('missing'),
                sortable: true,
                width: 10,
                id: 'missing'
            },{
                dataIndex: 'name_description',
                header: _t('name_description'),
                sortable: true,
                width: 10,
                id: 'name_description'
            },{
                dataIndex: 'name_label',
                header: _t('name_label'),
                sortable: true,
                width: 10,
                id: 'name_label'
            },{
                dataIndex: 'on_boot',
                header: _t('on_boot'),
                sortable: true,
                width: 10,
                id: 'on_boot'
            },{
                dataIndex: 'physical_utilisation',
                header: _t('physical_utilisation'),
                sortable: true,
                width: 10,
                id: 'physical_utilisation'
            },{
                dataIndex: 'read_only',
                header: _t('read_only'),
                sortable: true,
                width: 10,
                id: 'read_only'
            },{
                dataIndex: 'sharable',
                header: _t('sharable'),
                sortable: true,
                width: 10,
                id: 'sharable'
            },{
                dataIndex: 'type',
                header: _t('type'),
                sortable: true,
                width: 10,
                id: 'type'
            },{
                dataIndex: 'virtual_size',
                header: _t('virtual_size'),
                sortable: true,
                width: 10,
                id: 'virtual_size'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 10,
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

        ZC.VDIPanel.superclass.constructor.call(
            this, config);
    }
});

Ext.reg('VDIPanel', ZC.VDIPanel);

ZC.VIFPanel = Ext.extend(ZC.ZenPacks_zenoss_XenServer__Products_ZenModel_Device_DeviceComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'VIF',
            autoExpandColumn: 'name',
            sortInfo: {
                field: 'name',
                direction: 'asc',
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
                renderer: Zenoss.render.NetBotz_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'MAC',
                header: _t('MAC'),
                sortable: true,
                width: 10,
                id: 'MAC'
            },{
                dataIndex: 'MTU',
                header: _t('MTU'),
                sortable: true,
                width: 10,
                id: 'MTU'
            },{
                dataIndex: 'qos_algorithm_type',
                header: _t('qos_algorithm_type'),
                sortable: true,
                width: 10,
                id: 'qos_algorithm_type'
            },{
                dataIndex: 'status_code',
                header: _t('status_code'),
                sortable: true,
                width: 10,
                id: 'status_code'
            },{
                dataIndex: 'status_detail',
                header: _t('status_detail'),
                sortable: true,
                width: 10,
                id: 'status_detail'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 10,
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

        ZC.VIFPanel.superclass.constructor.call(
            this, config);
    }
});

Ext.reg('VIFPanel', ZC.VIFPanel);

ZC.VMPanel = Ext.extend(ZC.ZenPacks_zenoss_XenServer__Products_ZenModel_Device_DeviceComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'VM',
            autoExpandColumn: 'name',
            sortInfo: {
                field: 'name',
                direction: 'asc',
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
                renderer: Zenoss.render.NetBotz_entityLinkFromGrid,
                sortable: true
            },{
                dataIndex: 'VCPUs_max',
                header: _t('VCPUs_max'),
                sortable: true,
                width: 10,
                id: 'VCPUs_max'
            },{
                dataIndex: 'VCPUs_at_startup',
                header: _t('VCPUs_at_startup'),
                sortable: true,
                width: 10,
                id: 'VCPUs_at_startup'
            },{
                dataIndex: 'memory_dynamic_max',
                header: _t('memory_dynamic_max'),
                sortable: true,
                width: 10,
                id: 'memory_dynamic_max'
            },{
                dataIndex: 'memory_dynamic_min',
                header: _t('memory_dynamic_min'),
                sortable: true,
                width: 10,
                id: 'memory_dynamic_min'
            },{
                dataIndex: 'memory_overhead',
                header: _t('memory_overhead'),
                sortable: true,
                width: 10,
                id: 'memory_overhead'
            },{
                dataIndex: 'memory_static_max',
                header: _t('memory_static_max'),
                sortable: true,
                width: 10,
                id: 'memory_static_max'
            },{
                dataIndex: 'memory_static_min',
                header: _t('memory_static_min'),
                sortable: true,
                width: 10,
                id: 'memory_static_min'
            },{
                dataIndex: 'name_label',
                header: _t('name_label'),
                sortable: true,
                width: 10,
                id: 'name_label'
            },{
                dataIndex: 'name_description',
                header: _t('name_description'),
                sortable: true,
                width: 10,
                id: 'name_description'
            },{
                dataIndex: 'power_state',
                header: _t('power_state'),
                sortable: true,
                width: 10,
                id: 'power_state'
            },{
                dataIndex: 'uuid',
                header: _t('uuid'),
                sortable: true,
                width: 10,
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

        ZC.VMPanel.superclass.constructor.call(
            this, config);
    }
});

Ext.reg('VMPanel', ZC.VMPanel);


})();