(function() {
    "use strict";
    $(document).on('click', '.js_action_management .js_action_btn', function () {
        var self = $(this);
        var rqn_data = self.parents('.js_action_management').data();
        $('.front-console').addClass('loading');
        console.log(rqn_data.id);

        openerp.jsonRpc(
            '/purchase/console/' + rqn_data.id + '/' + self.data('name'), 'call',
            {'options': []})
            .then(function (data) {
                if (data.result === true){
                    console.log('ok... ');
                    console.log(data);
                    $('.front-console').removeClass('loading');
                    location.reload();
                }
                else if (data.result === false){
                    console.log('Not ok... ');
                    console.log(data);
                    $('.front-console').removeClass('loading');
                }
            }).fail(function (err, data) {
                console.log('Not ok... ');
                console.log(err);
                console.log(data);
                $('.front-console').removeClass('loading');
            });
    });

    jQuery.expr[":"].Contains = jQuery.expr.createPseudo(function(arg) {
        return function( elem ) {
            return jQuery(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
        };
    });

    $(document).on('keyup', '#search_box', function(e){
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
        console.log('##');
        var span = $(this);
        var input = span.next();
        input.show().removeAttr('disabled');
        input.focus();
        span.hide().attr({'disabled': 'disabled'});
    });

    $(document).on('keypress', '.rqn_line_display_name .rqn_line_polines .edit-input', function (event) {
        if (event.which == 13) {
            console.log('###');
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
                    span.text(input.val());
                }
                else if (data.result === false){
                }
            }).fail(function (err, data) {
            });
            span.show().removeAttr('disabled');
            input.hide().attr({'disabled': 'disabled'});
        }
    });
})();
