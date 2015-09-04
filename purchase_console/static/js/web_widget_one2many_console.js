openerp.purchase_console = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    /**
     * because is declared on One2ManyListView and we need to change some stuff here.
     * -
     * -
     * -
     */
    instance.web.form.One2ManyListConsole = instance.web.form.One2ManyList.extend({
        _add_row_class: 'oe_form_field_one2many_console'
    });

    /**
     * because is needed to overwrite One2ManyList and in the original is declared wired.
     * -
     * -
     * -
     */
    instance.web.form.One2ManyListViewConsole = instance.web.form.One2ManyListView.extend({
        //_template: 'One2Many.listview',
        init: function (parent, dataset, view_id, options) {
            console.log(' on my One2ManyListViewConsole to set One2ManyListConsole');
            this._super(parent, dataset, view_id, _.extend(options || {}, {
                ListType: instance.web.form.One2ManyListConsole
            }));
        }
    });

    /**
     * To Ensure my list: 'instance.web.form.One2ManyListViewConsole' is the one called.
     */
    instance.web.form.One2ManyViewManagerConsole = instance.web.form.One2ManyViewManager.extend({
        //template: 'One2Many.viewmanager',
        init: function (parent, dataset, views, flags) {
            console.log(' on my One2ManyListViewManagerConsole to set One2ManyListViewConsole');
            this._super(parent, dataset, views, _.extend({}, flags, {$sidebar: false}));
            this.registry = this.registry.extend({
                list: 'instance.web.form.One2ManyListViewConsole'
            });
        }
    });

    instance.purchase_console.FieldOne2ManyConsole = instance.web.form.FieldOne2Many.extend( {
        start: function() {
            this._super.apply(this, arguments);
            this.group_line = this.node.attrs.group_line;
            this.render_extra_rows();
        },
        /**
         * This Method is originally huge, but wired on it they call the view manager (which we need to over write on our
         * own widget, then overwrite the method to ensure only that our class is the one called.
         *
         * Every change with the original behavior should be commented inline to ensure a consistent documentation and
         * future migrations to new versions.
         *
         * @returns {*}
         */
        load_views: function() {
            var self = this;

            var modes = this.node.attrs.mode;
            modes = !!modes ? modes.split(",") : ["tree"];
            var views = [];
            _.each(modes, function(mode) {
                if (! _.include(["list", "tree", "graph", "kanban"], mode)) {
                    throw new Error(_.str.sprintf(_t("View type '%s' is not supported in One2Many."), mode));
                }
                var view = {
                    view_id: false,
                    view_type: mode == "tree" ? "list" : mode,
                    options: {}
                };
                if (self.field.views && self.field.views[mode]) {
                    view.embedded_view = self.field.views[mode];
                }
                if(view.view_type === "list") {
                    _.extend(view.options, {
                        addable: null,
                        selectable: self.multi_selection,
                        sortable: true,
                        import_enabled: false,
                        deletable: true
                    });
                    if (self.get("effective_readonly")) {
                        _.extend(view.options, {
                            deletable: null,
                            reorderable: false,
                        });
                    }
                } else if (view.view_type === "form") {
                    if (self.get("effective_readonly")) {
                        view.view_type = 'form';
                    }
                    _.extend(view.options, {
                        not_interactible_on_create: true,
                    });
                } else if (view.view_type === "kanban") {
                    _.extend(view.options, {
                        confirm_on_delete: false,
                    });
                    if (self.get("effective_readonly")) {
                        _.extend(view.options, {
                            action_buttons: false,
                            quick_creatable: false,
                            creatable: false,
                            read_only_mode: true,
                        });
                    }
                }
                views.push(view);
            });
            this.views = views;

            /**
             * Pointed to my class One2ManyViewManagerConsole
             * @type {instance.web.form.One2ManyViewManagerConsole}
             * @typeoriginal {instance.web.form.One2ManyViewManager}
             */
            console.log(' on my FieldOne2ManyConsole to set One2ManyViewManagerConsole');
            this.viewmanager = new instance.web.form.One2ManyViewManagerConsole(this, this.dataset, views, {});
            this.viewmanager.o2m = self;
            var once = $.Deferred().done(function() {
                self.init_form_last_update.resolve();
            });
            var def = $.Deferred().done(function() {
                self.initial_is_loaded.resolve();
            });
            this.viewmanager.on("controller_inited", self, function(view_type, controller) {
                controller.o2m = self;
                if (view_type == "list") {
                    if (self.get("effective_readonly")) {
                        controller.on('edit:before', self, function (e) {
                            e.cancel = true;
                        });
                        _(controller.columns).find(function (column) {
                            if (!(column instanceof instance.web.list.Handle)) {
                                return false;
                            }
                            column.modifiers.invisible = true;
                            return true;
                        });
                    }
                } else if (view_type === "form") {
                    if (self.get("effective_readonly")) {
                        $(".oe_form_buttons", controller.$el).children().remove();
                    }
                    controller.on("load_record", self, function(){
                         once.resolve();
                     });
                    controller.on('pager_action_executed',self,self.save_any_view);
                } else if (view_type == "graph") {
                    self.reload_current_view();
                }
                def.resolve();
            });
            this.viewmanager.on("switch_mode", self, function(n_mode, b, c, d, e) {
                $.when(self.save_any_view()).done(function() {
                    if (n_mode === "list") {
                        $.async_when().done(function() {
                            self.reload_current_view();
                        });
                    }
                });
            });
            $.async_when().done(function () {
                self.viewmanager.appendTo(self.$el);
            });
            return def;
        },
        /**
         * The place Holder for the columns on the console.
         */
        render_extra_rows: function(){
            var $extra_row = $(QWeb.render("purchase_console.FieldOne2ManyTdOne2Many", {
                colspan: this.count_fields(),
                content: 'Hello'
            }));
        },
        /**
         * Helper to set the colspan in the extra row which will be added.
         * @returns integer with length and number of columns.
         */
        count_fields: function(){
            var fieldarray = [];
            _.each(this.field.views.tree.arch.children, function(field){
                if (field.attrs.invisible){

                } else {
                    fieldarray.push(field);
                }
            });
            return fieldarray.length
        }
    });

    instance.web.form.widgets.add(
        'one2many_console',
        'instance.purchase_console.FieldOne2ManyConsole');
}

