$(function() {
    var AppView = Backbone.View.extend({
        el: $("body"),

        events: {
            "click [id$='init-partner-save']": "init_partner_save_form",

            "click [id$='item-save']": "item_save_form"
        },

        /*
        Saves both partner forms; init form and new/edit partner form

        :e: "Save" button on profile unit forms
         */
        init_partner_save_form: function(e) {

            // interrupts default functionality of the button with code below
            e.preventDefault();

            var form = $('#partner-form');

            var serialized_data = form.serialize();

            var get_data = window.location.search;
            if (get_data.length) {
                get_data = '&' + get_data.substr(1);
            }
            serialized_data += get_data;

            var company_id = $('[name=company_id]').val();

            $.ajax({
                type: 'POST',
                url: '/prm/view/save',
                data: serialized_data,
                success: function(data, status) {

                    if (data == ''){
                        if (status != 'prevent-redirect') {
                            window.location = '/prm/view?company=' + company_id;
                        }
                    } else {
                        // form was a json-encoded list of errors and error messages
                        var json = jQuery.parseJSON(data);

                        // remove color from labels of current errors
                        $('[class*=required]').parent().prev().removeClass('error-text');

                        // remove current errors
                        $('[class*=required]').children().unwrap();

                        if($.browser.msie){
                            $('[class*=msieError]').remove()
                        }

                        for (var index in json) {
                            var $error = $('[name="'+index+'"]');
                            var $labelOfError = $error.parent().prev();

                            // insert new errors after the relevant inputs
                            $error.wrap('<div class="required" />');
                            $error.attr("placeholder",json[index][0]);
                            $error.val('')
                            $labelOfError.addClass('error-text');
                        }
                    }
                }
            });
        },

        item_save_form: function(e){
            // interrupts default functionality of the button with code below
            e.preventDefault();

            var is_c_form_there = $('#contact-form').length;
            if (is_c_form_there > 0) {
                var form = $('#contact-form');
            }
            else {
                var form = $('#partner-form');
            }

            var serialized_data = form.serialize();

            var get_data = window.location.search;
            if (get_data.length) {
                get_data = '&' + get_data.substr(1);
            }
            serialized_data += get_data + '&ct=' + $('[name=ct]').val();

            var company_id = $('[name=company_id]').val();
            var partner_id = $('[name=partner_id]').val();

            $.ajax({
                type: 'POST',
                url: '/prm/view/details/save',
                data: serialized_data,
                success: function(data, status) {

                    if (data == ''){
                        if (status != 'prevent-redirect') {
                            window.location = '/prm/view/details?company=' + company_id + '&partner=' + partner_id;
                        }
                    } else {
                        // form was a json-encoded list of errors and error messages
                        var json = jQuery.parseJSON(data);

                        // remove color from labels of current errors
                        $('[class*=required]').parent().prev().removeClass('error-text');

                        // remove current errors
                        $('[class*=required]').children().unwrap();

                        if($.browser.msie){
                            $('[class*=msieError]').remove()
                        }

                        for (var index in json) {
                            var $error = $('[id$="-'+index+'"]');
                            var $labelOfError = $error.parent().prev();

                            // insert new errors after the relevant inputs
                            $error.wrap('<div class="required" />');
                            $error.attr("placeholder",json[index][0]);
                            $error.val('')
                            $labelOfError.addClass('error-text');
                        }
                    }
                }
            });
        }
    });

    var App = new AppView;
});
