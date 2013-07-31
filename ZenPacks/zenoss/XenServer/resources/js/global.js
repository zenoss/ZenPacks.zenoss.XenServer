(function(){

var ZC = Ext.ns('Zenoss.component');
var ZE = Ext.ns('Zenoss.extensions');


/* Friendly Names for Component Types ***************************************/

ZC.registerName('XenServerHost', _t('Host'), _t('Hosts'));
ZC.registerName('XenServerHostCPU', _t('Host CPU'), _t('Host CPUs'));
ZC.registerName('XenServerNetwork', _t('Network'), _t('Networks'));
ZC.registerName('XenServerPBD', _t('Physical Block Device'), _t('Physical Block Devices'));
ZC.registerName('XenServerPIF', _t('Physical NIC'), _t('Physical NICs'));
ZC.registerName('XenServerPool', _t('Pool'), _t('Pools'));
ZC.registerName('XenServerSR', _t('Storage Repository'), _t('Storage Repositories'));
ZC.registerName('XenServerVBD', _t('Virtual Block Device'), _t('Virtual Block Devices'));
ZC.registerName('XenServerVDI', _t('Virtual Disk'), _t('Virtual Disks'));
ZC.registerName('XenServerVIF', _t('Virtual NIC'), _t('Virtual NICs'));
ZC.registerName('XenServerVM', _t('VM'), _t('VMs'));
ZC.registerName('XenServerVMAppliance', _t('vApp'), _t('vApps'));


/* "Add XenServer" Dialog ***************************************************/

var add_xenserver = new Zenoss.Action({
    text: _t('Add XenServer') + '...',
    id: 'add_xenserver-item',
    permission: 'Manage DMD',
    handler: function(btn, e) {
        var win = new Zenoss.dialog.CloseDialog({
            width: 400,
            title: _t('Add XenServer'),
            items: [{
                xtype: 'form',
                buttonAlign: 'left',
                monitorValid: true,
                labelAlign: 'top',
                footerStyle: 'padding-left: 0',
                border: false,
                items: [{
                    xtype: 'textfield',
                    name: 'name',
                    fieldLabel: _t('Name'),
                    id: 'add_xenserver-name',
                    width: 260
                }, {
                    xtype: 'textfield',
                    name: 'address',
                    fieldLabel: _t('Address'),
                    id: 'add_xenserver-address',
                    width: 260
                }, {
                    xtype: 'textfield',
                    name: 'username',
                    fieldLabel: _t('Username'),
                    id: 'add_xenserver-username',
                    width: 260
                }, {
                    xtype: 'password',
                    name: 'password',
                    fieldLabel: _t('Password'),
                    id: 'add_xenserver-password',
                    width: 260
                }, {
                    xtype: 'combo',
                    width: 260,
                    name: 'collector',
                    fieldLabel: _t('Collector'),
                    id: 'add_xenserver-collector',
                    mode: 'local',
                    store: new Ext.data.ArrayStore({
                        data: Zenoss.env.COLLECTORS,
                        fields: ['name']
                    }),
                    valueField: 'name',
                    displayField: 'name',
                    forceSelection: true,
                    editable: false,
                    allowBlank: false,
                    triggerAction: 'all',
                    selectOnFocus: false,
                    listeners: {
                        'afterrender': function(component) {
                            var index = component.store.find('name', 'localhost');
                            if (index >= 0) {
                                component.setValue('localhost');
                            }
                        }
                    }
                }],
                buttons: [{
                    xtype: 'DialogButton',
                    id: 'add_xenserver-submit',
                    text: _t('Add'),
                    formBind: true,
                    handler: function(b) {
                        var form = b.ownerCt.ownerCt.getForm();
                        var opts = form.getFieldValues();

                        Zenoss.remote.XenServerRouter.add_xenserver(
                            opts,
                            function(response) {
                                if (response.success) {
                                    new Zenoss.dialog.SimpleMessageDialog({
                                        message: _t('XenServer discovery job created.'),
                                        buttons: [{
                                            xtype: 'DialogButton',
                                            text: _t('OK')
                                        }]
                                    }).show();
                                } else {
                                    new Zenoss.dialog.SimpleMessageDialog({
                                        message: response.msg,
                                        buttons: [{
                                            xtype: 'DialogButton',
                                            text: _t('OK')
                                            }]
                                    }).show();
                                    }
                            }
                        );
                    }
                }, Zenoss.dialog.CANCEL]
            }]
        });

        win.show();
    }
});

ZE.adddevice = ZE.adddevice instanceof Array ? ZE.adddevice : [];
ZE.adddevice.push(add_xenserver);

})();
