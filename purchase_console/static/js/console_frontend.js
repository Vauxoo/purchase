(function() {
    "use strict";
    console.log('All Loaded Ok!');
    $(document).on('click', '.js_action_management .js_action_btn', function () {
        var $data = $(this).parents(".js_publish_management");
        console.log($data);
        console.log($data.data('id'));

        /*
        var self=this;
        openerp.jsonRpc($data.data('id') || '/purchase/console/' + $data.data('id') + '/' + $data.data('name'), 'call',
            {})
            .then(function (result) {
                console.log('ok... ');
                console.log(result);
            }).fail(function (err, data) {
                console.log('Not ok... ');
                console.log(err);
                console.log(data);
            });
        */
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
