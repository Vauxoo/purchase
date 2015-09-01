openerp.purchase_console = function(instance)
{
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

            console.log(this);
            if (this.field.views.tree){
                var fields = this.field.views.tree.fields;
            }
            var data = [];
            _.map(fields, function(field, key){
                var cellh = $('<th>');

                cellh.text(field.string);
                cellh.appendTo(self.$('table.field_console thead tr'));
            });
            this.dataset.read_ids(show_value, fields).done(function(elements){
                _.each(elements, function (elem) {
                    var rowb = $('<tr>');

                    rowb.attr('data-id', elem.id);
                    _.map(fields, function (field, key){
                        var cellb = $('<td>');
                        if (field.type=='many2one'){
                            cellb.text(elem[key][1]);
                            cellb.appendTo(rowb);
                        } else {
                            cellb.text(elem[key]);
                            cellb.appendTo(rowb);
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
