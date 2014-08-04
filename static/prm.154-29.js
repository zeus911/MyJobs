$(document).ready(function() {
    /*
    Saves both partner forms; init form and new/edit partner form

    :e: "Save" button on profile unit forms
     */
    $('#init-partner-save').on("click", function(e) {
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
                        window.location = '/prm/view';
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
    });

    $('#item-save').on("click", function(e) {
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
                        window.location = '/prm/view/details?partner=' + partner_id;
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
                        $error.val('');
                        $labelOfError.addClass('error-text');
                    }
                }
            }
        });
    });

    $(".partner-tag").on("click", function() {
        if ($(this).children('i').hasClass('icon-ok')) {
            $(this).children('i').remove();
        } else {
            var i = document.createElement('i');
            $(i).addClass("icon icon-ok");
            $(this).append(i);
        }
    });

    $("#filter-partners").on("click", function() {
        /* Variables */
        var data = {},
            special_interest = [];

        /* Populating data */
        $(".partner-filters input").each(function() {
            if($(this).val()) {
                var data_key = $(this).prev('label').html().replace(":", "").toLowerCase();
                data[data_key] = $(this).val();
            }
        });
        // <i> is used for check icon
        $(".partner-tag:has(i)").each(function() {
            special_interest.push($(this).text().toLowerCase());
        });
        if(special_interest.length > 0)
            data.special_interest = special_interest;

        /* Ajax */
        $.ajax({
            type: 'GET',
            url: window.location.pathname,
            data: data,
            success: function(data) {
                console.log(data);
            }
        });
    });
});
