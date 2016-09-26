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
                }
            }).fail(function () {
                $('.front-console').removeClass('loading');
            });
    });

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


    $(document).on('dblclick', '.edit-span', function (){
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

    $(document).on('keypress', '.edit-input', function(event) {
        if ((event.which != 46 || $(this).val().indexOf('.') != -1) && (event.which < 48 || event.which > 57)) {
                event.preventDefault();
        }
    });

    openerp.website.if_dom_contains('.supplier-header', function(elements){
        var line_header = $(elements);
        var new_width = line_header.width() / line_header.find('.line-header').length;
        // The new width is increased because we're taking into account the padding-left and right
        $('.line-header, .order_line').width(new_width - 30);

    });


})();
