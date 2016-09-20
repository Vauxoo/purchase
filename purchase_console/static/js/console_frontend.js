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
            .then(function (result) {
                console.log('ok... ');
                console.log(result);
                $('.front-console').removeClass('loading');
                location.reload();
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
})();
