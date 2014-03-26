$(document).ready(function(){
    var offset = 0;

    var date_start = $('input[name=date_start]').attr('placeholder');
    var date_end = $('input[name=date_end]').attr('placeholder');

    $(".date-activity").click(function () {
        $(".date-range-select-form").toggleClass('date-range-select-form-visible');
    });

    $(this).ajaxStart(function () {
        // Disable errant clicks when an ajax request is active
        // Does not prevent the user from closing the modal
        $('button').attr('disabled', 'disabled');
        $('a.btn').attr('disabled', 'disabled');

        // Show ajax processing indicator
        $("#ajax-busy").show();
        $("#ajax-busy").show();   
    });
    $(this).ajaxStop(function () {
        // Allow button clicks when ajax request ends
        $('button').removeAttr('disabled');
        $('a.btn').removeAttr('disabled');

        // Hide ajax processing indicator
        $("#ajax-busy").hide();
        $(this).dialog("close");
    });
    $(this).ajaxError(function (e, xhr) {
        if (xhr.status == 403) {
            // redirect to the home page on 403
            window.location = '/';
        }
    });
    
    /*Explicit control of main menu, primarily for mobile but also provides
    non hover and cover option if that becomes an issue.*/
    $("#nav .main-nav").click(function(e){
        e.preventDefault();
        
        $("#nav").toggleClass("active");
        $(".company-nav-item").addClass("no-show");
        $(".settings-nav-item").addClass("no-show");
        $("#back-btn-li").addClass("no-show");
        
        $("#logged-in-li").removeClass("no-show");
        $("#profile-link").removeClass("no-show");
        $("#savedsearch-link").removeClass("no-show");
        $("#candidate-link").removeClass("no-show");
        $("#candidate-link-one").removeClass("no-show"); 
        $('#settings-link').removeClass("no-show");
    });

    $("#pop-menu").mouseleave(function(){
        $("#nav").removeClass("active");
    });   
    
    // Handles sub-menu displaying/hiding.
    $('#candidate-link').click(function(e) {
        $(".company-nav-item").removeClass("no-show");
        $("#back-btn-li").removeClass("no-show");
        
        $("#settings-link").addClass("no-show");
        $("#logged-in-li").addClass("no-show");
        $("#profile-link").addClass("no-show");
        $("#savedsearch-link").addClass("no-show");
        $("#candidate-link").addClass("no-show");
        $("#candidate-link-one").addClass("no-show");
        $("#partner-link").addClass("no-show");
        $("#partner-link-one").addClass("no-show");
        $("#account-link").addClass("no-show");
        $("#logout-link").addClass("no-show"); 
    });
    $('#partner-link').click(function(e) {
        $(".partner-nav-item").removeClass("no-show");
        $("#back-btn-li").removeClass("no-show");

        $("#settings-link").addClass("no-show");
        $("#logged-in-li").addClass("no-show");
        $("#profile-link").addClass("no-show");
        $("#savedsearch-link").addClass("no-show");
        $("#candidate-link").addClass("no-show");
        $("#candidate-link-one").addClass("no-show");
        $("#partner-link").addClass("no-show");
        $("#partner-link-one").addClass("no-show");
        $("#account-link").addClass("no-show");
        $("#logout-link").addClass("no-show");
    });
    $('#settings-link').click(function(e) {
        $(".settings-nav-item").removeClass("no-show");
        $("#back-btn-li").removeClass("no-show");
        
        $("#settings-link").addClass("no-show");
        $("#logged-in-li").addClass("no-show");
        $("#profile-link").addClass("no-show");
        $("#savedsearch-link").addClass("no-show");
        $("#candidate-link").addClass("no-show");
        $("#candidate-link-one").addClass("no-show");
        $("#partner-link").addClass("no-show");
        $("#partner-link-one").addClass("no-show");
        $("#account-link").addClass("no-show");
        $("#logout-link").addClass("no-show"); 
    });    
    $("#back-btn").click(function(e){
        e.preventDefault();
        
        $(".company-nav-item").addClass("no-show");
        $(".partner-nav-item").addClass("no-show");
        $(".settings-nav-item").addClass("no-show");
        $("#back-btn-li").addClass("no-show");
        
        $("#logged-in-li").removeClass("no-show");
        $("#profile-link").removeClass("no-show");
        $("#savedsearch-link").removeClass("no-show");
        $("#candidate-link").removeClass("no-show");
        $("#candidate-link-one").removeClass("no-show");
        $("#partner-link").removeClass("no-show");
        $("#partner-link-one").removeClass("no-show");
        $("#settings-link").removeClass("no-show"); 
    });

    // Displays/hides and highlights/unhighlights candidate and partner
    // dropdown depending on hover.
    $("#company-dropdown").mouseover(function(){
        $("#company-menu").removeClass("no-show");
        $("#candidate-tab").addClass("show");
    });
    $("#company-dropdown").mouseleave(function(){
        $("#company-menu").addClass("no-show");
        $("#candidate-tab").removeClass("show");
    });
    $("#partner-dropdown").mouseover(function(){
        $("#partner-menu").removeClass("no-show");
        $("#partner-tab").addClass("show");
    });
    $("#partner-dropdown").mouseleave(function(){
        $("#partner-menu").addClass("no-show");
        $("#partner-tab").removeClass("show");
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

    $('[class*=mymessage-]').click(function(){
        readMessage(this);
    });

    if($(window).width() < 500){
        addBackButton();
    }

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
});

function addBackButton(){
    $('.topbar-inner').find('.span1').prepend('<a id="topbar-back" class="desktop_hide" href="#" onclick="javascript:window.history.back(-1);return false;"><span id="prm-arrow-left"></span></a>');
}

function readMessage(button){
    var message_box = $(button);
    var name = $(button).attr('class').split(' ').pop();
    var csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    var data = "name="+name+"&csrfmiddlewaretoken="+csrf_token;
    $.ajax({
        type: 'POST',
        url: '/message/',
        data: data,
        dataType: 'json',
        success: function(data) {
            message_box.parent().hide();
        }
    })
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

window.dateFormat = 'dd-M-yy';
