(function() {
    "use strict";
    $(document).on('click', '.js_action_management .js_action_btn', function () {
        var self = $(this);
        var rqn_data = self.parents('.js_action_management').data();
        $('.front-console').addClass('loading');

        openerp.jsonRpc(
            '/purchase/console/' + rqn_data.id + '/' + self.data('name'), 'call',
            {'options': []})
            .then(function (data) {
                if (data.result === true){
                    $('.front-console').removeClass('loading');
                    location.reload();
                }
                else if (data.result === false){
                    $('.front-console').removeClass('loading');
                    display_msg_error(data.message);
                }
            }).fail(function () {
                $('.front-console').removeClass('loading');
            });
    });

    // Searching product line  Feature
    jQuery.expr[":"].Contains = jQuery.expr.createPseudo(function(arg) {
        return function( elem ) {
            return jQuery(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
        };
    });
    $(document).on('keyup', '#search_box', function(){
        var change_text = $(this).val();
        $("tr[id*='line_item_']").show();
        $("#search_summary").removeClass('invisible');
        if (change_text) {
            var items_result = $("tr[id*='line_item_'].rqn_line_display_name:Contains("+change_text+")");
            $("#search_number").text(items_result.length);
            $("tr[id*='line_item_'].rqn_line_display_name:not(:Contains("+change_text+"))")
                .hide().next('.rqn_line_values').hide();
        } else {
            $("#search_summary").addClass('invisible');
        }
        event.preventDefault();
    });


    // Edition of the values of the cell options
    $(document).on('dblclick', '.edit-span', function (){
        // Hide all the other inputs if them
        $('.edit-input').hide().attr({'disabled': 'disabled'});
        $('.edit-span').show().removeAttr('disabled');

        // Only hide the span where the dbclick was trigger and show the input
        // hidden
        var span = $(this);
        var input = span.next();
        input.show().removeAttr('disabled');
        input.focus();
        span.hide().attr({'disabled': 'disabled'});
    });
    $(document).on('keypress', '.rqn_line_display_name .rqn_line_polines .edit-input', function (event) {
        if (event.which == 13) {
            var input = $(this);
            var name = input.attr('name');
            var id = input.parents('.order_line').attr('id');
            var span = input.parent().find('span');

            openerp.jsonRpc(
                '/update/line/' + id, 'call',
                {
                    'id': id,
                    'name': name,
                    'value': input.val()
                }).then(function (data) {
                    if (data.result === true){
                        var value = parseFloat(input.val()).toFixed(1);
                        span.text(value);
                        input.val(value);
                    }
                    else if (data.result === false){
                        span.text('XX');
                    }
                }).fail(function () {
                });
            span.show().removeAttr('disabled');
            input.hide().attr({'disabled': 'disabled'});
        }
    });
    // Preventing insert different values from numeric values
    $(document).on('keypress', '.edit-input', function(event) {
        if ((event.which != 46 || $(this).val().indexOf('.') != -1) && (event.which < 48 || event.which > 57)) {
                event.preventDefault();
        }
    });

    //Setting the width of columns
    openerp.website.if_dom_contains('.supplier-header', function(elements){
        var line_header = $(elements);
        var new_width = line_header.width() / line_header.find('.line-header').length;
        // The new width is increased because we're taking into account the padding-left and right
        $('.line-header, .order_line').width(new_width - 50);
    });

    // Check and uncheck the check box in option lines
    $(document).on('click', 'div.input-checkbox input', function() {
        $(this).parents('.order_line').toggleClass('inpunt-check');
        var input = $(this);
        var name = input.attr('name');
        var id = input.parents('.order_line').attr('id');

        openerp.jsonRpc(
            '/purchase_console/action-line/', 'call',
            {
                'line_id': parseInt(id, 10),
                'name': name,
                'value': input.prop('checked')
            }).then(function (data) {
                if (data.result === true){
                }
                else if (data.result === false){
                }
            }).fail(function () {
            });
    });

    // Button approve
    $(document).on('click', '.btn-approve', function() {
        var order_id = parseInt($(this).next('a').data('order_id'), 10);
        $('.front-console').addClass('loading');
        openerp.jsonRpc(
            '/purchase_console/order_approve/', 'call',
            {
                'order_id': order_id,
            }).then(function (data) {
                if (data.result === true){
                    $('.front-console').removeClass('loading');
                    location.reload();
                }
                else if (data.result === false){
                    $('.front-console').removeClass('loading');
                }
            }).fail(function () {
            });
    });

    // Modal displaying when clicking the image partner
    $(document).on('click', '.line-header a', function(event) {
        event.preventDefault();
            var order_id = parseInt($(this).data('order_id'), 10);
            openerp.jsonRpc('/shop/purchase_order_modal/' + order_id, 'call', {})
                .then(function (view_modal) {
                    var modal = $(view_modal);
                    modal.appendTo($('.tab-content'))
                        .modal()
                        .on('hidden.bs.modal', function () {
                            // When modal close
                            $(this).remove();
                        });

                    modal.on('click', '.a-submit.a-cancel', function () {
                        modal.modal('hide');
                    });
                    modal.on('click', 'button.row_delete', function () {
                        var line = $(this).parents('tr');
                        var line_id = parseInt(line.data('line_id'), 10);
                        openerp.jsonRpc(
                            '/purchase_console/remove-line/', 'call',
                            {'line_id': line_id})
                            .then(function (data) {
                                if (data === true){
                                    line.remove();
                                    $('.rqn_line_polines div[id="'+ line_id +'"]').empty().append("&nbsp;");
                                }
                            });
                    });
                });
            return false;
        });

    function display_msg_error(message){
        openerp.jsonRpc('/shop/modal_msg_error/', 'call', {
            'message': message,
        }).then(function (view_modal) {
            var modal = $(view_modal);
            modal.appendTo($('.tab-content')).modal()
                .on('hidden.bs.modal', function () {
                    // When modal close
                    $(this).remove();
                });
            setTimeout(function(){
                modal.modal('hide');
            }, 3000);
            });
    }

})();
