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
            console.log(this.model_requisition);
            this.create_form_fields = {
                supplier_ids: {
                    id: "supplier_ids",
                    index: 2,
                    corresponding_property: "supplier_ids",
                    label: _t("Suppliers"),
                    required: false,
                    tabindex: 1,
                    constructor: instance.web.form.FieldMany2ManyTags,
                    field_properties: {
                        relation: "res.partner",
                        string: _t("Suppliers"),
                        type: "many2many",
                        domain: [['is_company','=',true]]
                    },
                },
            };
        },

        start: function() {
            var self = this,
                deferred_promises = [];

            this._super();

            // Working on specified purchase requisitions(s)
            if (self.requisition_id) {            // Get the function to format currencies
                deferred_promises.push(self.model_requisition
                    .call("read", [ [self.requisition_id], ['name', 'line_ids', 'vendors', 'state'] ])
                    .then(function(data) {
                        self.requisition = data;
                    })
                );
            }
            return $.when.apply($, deferred_promises).then(function(){
                // Render and display
                console.log(self.requisition);
                self.$('.info_header_left').prepend(QWeb.render("purchase_console.header_left", {
                    lines: self.requisition[0].line_ids.length,
                    name: self.requisition[0].name,
                }));
                self.$('.info_header_right').prepend(QWeb.render("purchase_console.header_right", {
                    lines: self.requisition[0].line_ids.length,
                    vendors: self.requisition[0].vendors,
                }));
                self.$('.content_placeholder').prepend(QWeb.render("purchase_console.table_content", {
                    lines: self.requisition[0].line_ids.length,
                    line_ids: self.requisition[0].line_ids,
                }));
                self.$('.buttons_placeholder').prepend(QWeb.render("purchase_console.action_buttons", {
                    lines: self.requisition[0].line_ids.length,
                    widget: this,
                }));
            }).always(function(){
                self.render();
            })
        },
        /* create form widgets, append them to the dom and bind their events handlers */
        createFormWidgets: function() {
            var self = this;
            var create_form_fields = self.getParent().create_form_fields;
            var create_form_fields_arr = [];
            for (var key in create_form_fields)
                if (create_form_fields.hasOwnProperty(key))
                    create_form_fields_arr.push(create_form_fields[key]);
            create_form_fields_arr.sort(function (a, b) {
                return b.index - a.index
            });

            // field_manager
            var dataset = new instance.web.DataSet(this, "purchase.requisition", self.context);
            dataset.ids = [];
            dataset.arch = {
                attrs: {string: "Naguevona Lo deseo", version: "7.0", class: "oe_form_container"},
                children: [],
                tag: "form"
            };

            var field_manager = new instance.web.FormView(
                this, dataset, false, {
                    initial_mode: 'edit',
                    disable_autofocus: false,
                    $buttons: $(),
                    $pager: $()
                });

            field_manager.load_form(dataset);

            // fields default properties
            var Default_field = function() {
                this.context = {};
                this.domain = [];
                this.help = "";
                this.readonly = false;
                this.required = true;
                this.selectable = true;
                this.states = {};
                this.views = {};
            };
            var Default_node = function(field_name) {
                this.tag = "field";
                this.children = [];
                this.required = true;
                this.attrs = {
                    invisible: "False",
                    modifiers: '{"required":true}',
                    name: field_name,
                    nolabel: "True",
                };
            };

            // Append fields to the field_manager
            field_manager.fields_view.fields = {};
            for (var i=0; i<create_form_fields_arr.length; i++) {
                field_manager.fields_view.fields[create_form_fields_arr[i].id] = _.extend(new Default_field(), create_form_fields_arr[i].field_properties);
            }
            field_manager.fields_view.fields["change_partner"] = _.extend(new Default_field(), {
                relation: "res.partner",
                string: _t("Partner"),
                type: "many2one",
                domain: [['parent_id','=',false], '|', ['customer','=',true], ['supplier','=',true]],
            });

            // Returns a function that serves as a xhr response handler
            var hideGroupResponseClosureFactory = function(field_widget, $container, obj_key){
                return function(has_group){
                    if (has_group) $container.show();
                    else {
                        field_widget.destroy();
                        $container.remove();
                        delete self[obj_key];
                    }
                };
            };

            // generate the create "form"
            self.create_form = [];
            for (var i=0; i<create_form_fields_arr.length; i++) {
                var field_data = create_form_fields_arr[i];

                // create widgets
                var node = new Default_node(field_data.id);
                if (! field_data.required) node.attrs.modifiers = "";
                var field = new field_data.constructor(field_manager, node);
                self[field_data.id+"_field"] = field;
                self.create_form.push(field);

                // on update : change the last created line
                field.corresponding_property = field_data.corresponding_property;
                field.on("change:value", self, self.formCreateInputChanged);

                // append to DOM
                var $field_container = $(QWeb.render("form_create_field", {id: field_data.id, label: field_data.label}));
                field.appendTo($field_container.find("td"));
                self.$(".create_form").prepend($field_container);

                // now that widget's dom has been created (appendTo does that), bind events and adds tabindex
                if (field_data.field_properties.type != "many2one") {
                    // Triggers change:value TODO : moche bind ?
                    field.$el.find("input").keyup(function(e, field){ field.commit_value(); }.bind(null, null, field));
                }
                field.$el.find("input").attr("tabindex", field_data.tabindex);

                // Hide the field if group not OK
                if (field_data.group !== undefined) {
                    var target = $field_container;
                    target.hide();
                    self.model_res_users
                        .call("has_group", [field_data.group])
                        .then(hideGroupResponseClosureFactory(field, target, (field_data.id+"_field")));
                }
            }

            // generate the change partner "form"
            var change_partner_node = new Default_node("change_partner"); change_partner_node.attrs.modifiers = "";
            self.change_partner_field = new instance.web.form.FieldMany2ManyTags(field_manager, change_partner_node);
            self.change_partner_field.appendTo(self.$(".change_partner_container"));
            self.change_partner_field.on("change:value", self.change_partner_field, function() {
                // self.changePartner(this.get_value());
                console.log('Partner Changed');
            });

            field_manager.do_show();
        },
        render: function() {
            var self = this;
            console.log('On Render');
            self.createFormWidgets();
        },
    });

};