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
})();
