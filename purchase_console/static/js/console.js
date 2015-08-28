openerp.purchase_console = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.web.purchase_console = instance.web.purchase_console || {};
    instance.web.client_actions.add(
        'console_homepage', 'instance.web.purchase_console.HomePage');
    instance.web.purchase_console.HomePage = instance.web.Widget.extend({
        className: 'oe_requisition_console',
        template: 'purchase_console.console',
        init: function(parent, context) {
            this._super(parent);
            this.model_requisition = new instance.web.Model("purchase.requisition");
            this.actions = new instance.web.Model("ir.actions.actions");
            this.context = context.context;
            if (context.context.active_id) this.requisition_id = context.context.active_id;
            console.log(this);
            console.log(context);
        },
        start: function() {
            var self = this,
                deferred_promises = [];

            this._super();

            // Working on specified purchase requisitions(s)
            if (self.requisition_id) {

            }
        },
        render: function() {
            console.log('On Render');
        },
    });

};