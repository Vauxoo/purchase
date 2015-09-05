openerp.purchase_console = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.web.list.One2manyColumns = instance.web.list.Column.extend({
        format: function (row_data, options) {
            var self = this;
            if (!row_data[this.id] || !row_data[this.id].value) {
                return 'No Data';
            }
            var value = row_data[this.id].value;
            if (this.type === 'one2many') {
                //Ugly should it be dynamic?
                var fields = ['name', 'last_price', 'price_unit',
                    'price_bid', 'accounting_cost', 'last_invoice_id', 'partner_id'];
                // temp empty value
                self.elements = [];
                self.placeholder = instance.web.qweb.render('ListView.row.one2many_columns_place',
                                                {widget: self, record: row_data});
                self.dataset = new instance.web.Model(self.relation)
                    .call('read', [value, fields, self.context]).done(function (datas) {
                        self.elements = datas

                    });
                    promise = $.when(self.dataset).then( function(){
                        content = instance.web.qweb.render('ListView.row.one2many_columns', {widget: self});
                        $('.' + self.name + '_' + row_data.id.value).html(content);
                    });

                return self.placeholder
            }
        }
    });
    instance.web.list.columns.add('field.one2many_columns', 'instance.web.list.One2manyColumns');
}