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
            this.context = context;
            console.log(context);
        },
        start: function() {
            this._super();
            var deferred_promises = [];

            // Working on specified purchase(s)
            if (self.statement_ids && self.statement_ids.length > 0) {

            }
        },
        render: function() {
            console.log('On Render');
        },
    });

};