openerp.purchase_console = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.web.form.widgets.add(
        'one2many_console',
        'instance.purchase_console.FieldOne2ManyConsole');
    instance.purchase_console.FieldOne2ManyConsole = instance.web.form.AbstractField.extend( {
        template: 'FieldOne2ManyConsole',
        init: function (field_manager, node) {
            this._super(field_manager, node);
            this.dataset = new instance.web.form.One2ManyDataSet(this, this.field.relation);
            this.dataset.o2m = this;
            this.dataset.parent_view = this.view;
            this.dataset.child_name = this.name;
            this.set_value([]);
            this.attrs = node.attrs;
        },
        start: function() {
            this.render_value(this, arguments);
        },
        get_value: function () {
            var value = this.get('value');
            return value
        },
        render_value: function(){
            var self = this,
                show_value = this.get_value();
            if (this.field.views.tree){
                var fields = this.field.views.tree.fields;
            }
            var data = [];
            var fieldarray = [];
            _.map(fields, function(field, key){
                var cellh = $('<th>');
                cellh.text(field.string);
                cellh.appendTo(self.$('table.field_console thead tr'));
                fieldarray.push(field);
            });
            this.dataset.read_ids(show_value, fields).done(function(elements){
                _.each(elements, function (elem) {
                    var rowb = $('<tr>');

                    rowb.attr('data-id', elem.id);
                    _.map(fields, function (field, key){
                        var cellb = $('<td>');
                        if (field.type=='many2one') {
                            cellb.text(elem[key][1]);
                            cellb.appendTo(rowb);
                        }
                        else if (field.type=='one2many'){
                            if (field.views.tree){
                                var fields_o2m = field.views.tree.fields;
                            }
                            NewDatase = new instance.web.form.One2ManyDataSet(this, field.relation);
                            NewDatase.o2m = self;
                            NewDatase.read_ids(elem[key], fields_o2m).done(function(rfqs){
                                _.each(rfqs, function(rfq){
                                    var rowc = $('<tr>'),
                                        cellc = $('<td>');
                                        cellc.attr('colspan', fieldarray.length);
                                        rowc.attr('data-id', rfq.id);
                                        rowc.attr('data-model', field.relation);
                                    _.map(fields_o2m, function(f, po_key){
                                        if (f.type=='many2one') {
                                            var $contentcellc = $(QWeb.render("FieldOne2ManyTdMany2One", {content: rfq[po_key][1]}));
                                            $contentcellc.appendTo(cellc);
                                        }
                                        else if (f.type=='one2many'){
                                            var $contentcellc = $(QWeb.render("FieldOne2ManyTdOne2Many", {content: rfq[po_key].length}));
                                            $contentcellc.appendTo(cellc);
                                        } else {
                                            var $contentcellc = $(QWeb.render("FieldOne2ManyTdText", {content: rfq[po_key]}));
                                            $contentcellc.appendTo(cellc);
                                        }
                                    });
                                cellc.appendTo(rowc);
                                rowc.appendTo(self.$('table.field_console tbody'));
                                });
                            });
                            var show_m2o = $('<span><a href="#" class="btn btn-link"><i class="fa fa-plus-circle"></i> '+elem[key].length+'</a></span>');
                            show_m2o.appendTo(cellb);
                            cellb.appendTo(rowb);
                        } else {
                            cellb.text(elem[key]);
                            cellb.appendTo(rowb);;
                        }
                    });
                    rowb.appendTo(self.$('table.field_console tbody'));
                });
            });
        },
        destroy: function () {
            return this._super();
        },
    });
}
