openerp.purchase_console = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.web.list.One2manyColumns = instance.web.list.Column.extend({
        init: function (id, tag, attrs) {
            _.extend(attrs, {
                id: id,
                tag: tag,
            });
            this.modifiers = attrs.modifiers ? JSON.parse(attrs.modifiers) : {};
            delete attrs.modifiers;
            _.extend(this, attrs);
            if (this.modifiers['tree_invisible']) {
                this.invisible = '1';
            } else { delete this.invisible; }
        },

        format: function (row_data, options) {
            var self = this;
            if (!row_data[this.id] || !row_data[this.id].value) {
                return 'No Data';
            }
            var value = row_data[this.id].value;
            if (this.type === 'one2many') {
                //Ugly should it be dynamic?
                var fields = ['name', 'last_price', 'price_unit', 'product_qty',
                    'price_bid', 'accounting_cost', 'last_invoice_id', 'partner_id'];
                // temp empty value
                self.elements = [];
                self.placeholder = instance.web.qweb.render('ListView.row.one2many_columns_place',
                                                {widget: self, record: row_data});
                self.partners = [];
                self.dataset = new instance.web.Model(self.relation)
                    .call('read', [value, fields, self.context]).done(function (datas) {
                        self.elements = datas;
                    }).done(function(datas){
                        //Set the header
                        //TODO: fix the ugly hack using partners directly
                        _.each(self.elements, function(ele){
                            var self_each = this;
                            self_each.is_there=false;
                            _.each(self.partners, function(partner){
                                if (partner[0] == ele.partner_id[0]) {
                                    self_each.is_there = true;
                                }
                            });
                            if (!self_each.is_there){
                                self.partners.push(ele.partner_id);
                            }
                        });
                    });
                    promise = $.when(self.dataset).then( function(){
                        //TODO: Resolver como precrear columnas vacías de partners.
                        content = instance.web.qweb.render('ListView.row.one2many_columns', {widget: self, partners: self.partners});
                        $('.' + self.name + '_' + row_data.id.value).html(content);
                        header = instance.web.qweb.render('ListView.row.one2many_headers', {widget: self, partners: self.partners});
                        $("th[data-id='po_line_ids']").html(header);
                    });

                return self.placeholder
            }
        }
    });
    instance.web.list.columns.add('field.one2many_columns', 'instance.web.list.One2manyColumns');
}
