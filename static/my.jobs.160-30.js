$(document).ready(function(){
    var offset = 0;

    var date_start = $('input[name=date_start]').attr('placeholder');
    var date_end = $('input[name=date_end]').attr('placeholder');

    $(".date-activity").click(function () {
        $(".date-range-select-form").toggleClass('date-range-select-form-visible');
    });

    var $loader = $("#ajax-busy"), timer;
    $loader.hide()
        .ajaxStart(function() {
            timer && clearTimeout(timer);
            timer = setTimeout(function() {
                // Disable errant clicks when an ajax request is active
                $('button').attr('disabled', 'disabled');
                $('a.btn').attr('disabled', 'disabled');

                // Show ajax processing indicator
                $loader.show();
            }, 1000);
        })
        .ajaxStop(function() {
            // Allow button clicks when ajax request ends
            $('button').removeAttr('disabled');
            $('a.btn').removeAttr('disabled');

            clearTimeout(timer);
            $loader.hide();
        })
        .ajaxError(function (e, xhr) {
            if (xhr.status == 403) {
                // redirect to the home page on 403
                window.location = '/';
            }
        });

    $('#disable-account').click(function(){
        var answer = confirm('Are you sure you want to disable your account?');
        if (answer == true) {
            window.location = '/account/disable';
        }
    });

    $('a.account-menu-item').click(function(e) {
        e.preventDefault();
        if ($(window).width() < 500) {
            $('div.settings-nav').hide();
            $('div.account-settings').show();
        }
    });

    $(function() {
        $('input, textarea').placeholder();
    });

    $('#captcha-form').submit(function(e) {
        e.preventDefault();
        contactForm();
    });

    $('[class*=mymessage-read-]').click(function(){
        readMessage(this);
    });

    $('#delete').hover(function(e){
        $.ajax({
            global: false,
            url: static_url + "bootstrap/bootstrap-modalmanager.js",
            dataType: "script",
            cache: true
        });
        $.ajax({
            global: false,
            url: static_url + "bootstrap/bootstrap-modal.js",
            dataType: "script",
            cache: true
        });
        $(this).unbind('mouseenter mouseleave');
    });

    if($('[id$="country_code"]').length){
        moveCountrySelection();
    }
});

function readMessage(button){
    var message_box = $(button),
        name = message_box.attr('class').split(' ').pop(),
        data = "name="+name;
    $.ajax({
        type: 'GET',
        url: '/message/',
        data: data,
        dataType: 'json',
        success: function(data) {
            if (typeof on_read === "undefined") {
                message_box.parent().hide();
            } else {
                on_read(message_box);
            }
        }
    });
}

function clearForm(form) {
    // clear the inputted form of existing data
    $(':input', form).each(function() {
        var type = this.type;
        var tag = this.tagName.toLowerCase(); // normalize case
        if (type == 'text' || type == 'password' || tag == 'textarea')
            this.value = "";
        else if (type == 'checkbox' || type == 'radio')
            this.checked = false;
        else if (tag == 'select')
            this.selectedIndex = -1;
    });
}

function moveCountrySelection() {
    var country_label = $("label[for$='-country_code']");
    country_label.unwrap();
    country_label.insertBefore(country_label.parent());
    country_label.wrap("<div class='span3 form-label pull-left'></div>");
}

// Validation for contact form
function contactForm(){
    var form = $('#captcha-form');
    var data = form.serialize();
    $.ajax({
        type: 'POST',
        url: '/contact/',
        data: data,
        dataType: 'json',
        success: function(data) {
            if(data.validation == 'success'){
                $('#contact-us-form').hide('slide', {direction: 'left'}, 250);
                setTimeout(function(){
                    $('#success-info').show('slide', {direction: 'right'}, 250);
                    $('.formBox').show('slide', {direction: 'right'}, 250);
                }, 300);
                $('#name-input').html(data.name);
                $('#email-input').html(data.c_email);
                if(data.phone == ''){
                    $('#phone-input').html('Not provided');
                }else{
                    $('#phone-input').html(data.phone);
                }
                $('#iam-input').html(data.c_type);
                $('#aoi-input').html(data.reason);
                $('#comment-input').html(data.comment);
                $('#time-input').html(data.c_time);
            }else{
                var required = $('[class*=required]');
                // remove color from labels of current errors
                required.prev().removeClass('required-label');

                // remove border around element
                required.children().removeClass('required-border');

                // remove current errors
                required.children().unwrap();

                if($.browser.msie){
                    $('[class*=msieError]').remove()
                }
                for (var index in data.errors) {
                    var $error = $('[class$="'+data.errors[index][0]+'"]');
                    var $field = $('[id$=recaptcha_response_field]')
                    var $labelOfError = $error.prev();
                    // insert new errors after the relevant inputs
                    $error.wrap('<div class="required" />');
                    $error.addClass('required-border')
                    if(!($.browser.msie)){
                        $field.attr("placeholder",data.errors[index][1]);
                        $field.val('');
                    }else{
                        field = $error.parent();
                        field.before("<div class='msieError'><i>" + data.errors[index][1] + "</i></div>");
                    }
                    $labelOfError.addClass('required-label')
                }
            }
        }
    });
}

function accordion(header, contents) {
    $(header).on('click', function() {
        $(this).next($(contents)).slideToggle();
    });
}

window.dateFormat = 'dd-M-yy';
