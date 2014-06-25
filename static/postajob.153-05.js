if(typeof jQuery == 'undefined') {
    var script = document.createElement('script');
    script.type = "text/javascript";
    script.src = "//d2e48ltfsb5exy.cloudfront.net/framework/v2/secure/js/code/jquery-1.7.1.min.js";
    document.getElementsByTagName('head')[0].appendChild(script);
}

window.onload = function(){
    update_apply_fields();
    update_site_fields();
    update_job_limit_fields();
    add_refresh_btn();

    // Job Form
    $(document).on("change", '#id_apply_type_0', function(){
        update_apply_fields();
    });
    $(document).on("change", '#id_apply_type_1', function(){
        update_apply_fields();
    });
    $(document).on("change", '#id_apply_type_2', function(){
        update_apply_fields();
    });
    $(document).on("change", '#post-to-selector_0', function() {
        update_site_fields();
    });
    $(document).on("change", '#post-to-selector_1', function() {
        update_site_fields();
    });

    // Product Form
    $(document).on("change", '#id_job_limit_0', function() {
        update_job_limit_fields();
    });
    $(document).on("change", '#id_job_limit_1', function() {
        update_job_limit_fields();
    });

    // OfflinePurchase Form
    $(".refresh").on("click", function(e) {
        validate_company_user(e)
    });
    $("#id_existing_user").on("input keypress cut paste", function(e) {
        validate_company_user(e)
    });
};


function hide_field(field_name) {
    $('.' + field_name + '-label').hide();
    $('.' + field_name + '-field').hide();
}


function hide_admin_field(field_name) {
    $('.field-' + field_name).hide();
}


function show_field(field_name) {
    $('.' + field_name + '-label').show();
    $('.' + field_name + '-field').show();
}


function show_admin_field(field_name) {
    $('.field-' + field_name).show();
}


function clear_input(field_name) {
    $('#id_' + field_name).val('');
}


function update_apply_fields() {
    if($('#id_apply_type_0').is(':checked')) {
        show_field('apply-link');
        show_admin_field('apply_link')

        clear_input('apply_email');
        clear_input('apply_info');

        hide_admin_field('apply_email');
        hide_admin_field('apply_info');
        hide_field('apply-email');
        hide_field('apply-instructions');
    }
    else if($('#id_apply_type_1').is(':checked')) {
        show_field('apply-email');
        show_admin_field('apply_email');

        clear_input('apply_info');
        clear_input('apply_link');

        hide_admin_field('apply_link');
        hide_admin_field('apply_info');
        hide_field('apply-link');
        hide_field('apply-instructions');
    }
    else {
        show_field('apply-instructions');
        show_admin_field('apply_info');

        clear_input('apply_email');
        clear_input('apply_link');

        hide_admin_field('apply_link');
        hide_admin_field('apply_email');
        hide_field('apply-link');
        hide_field('apply-email');
    }
}


function update_site_fields() {
    if($('#post-to-selector_0').is(':checked')) {
        hide_field('site');
        hide_admin_field('site_packages');
    }
    else {
        show_field('site');
        show_admin_field('site_packages');
    }
}


function update_job_limit_fields() {
    if($('#id_job_limit_0').is(':checked')) {
        hide_field('number-of-jobs');
        hide_admin_field('num_jobs_allowed');
    }
    else {
        show_field('number-of-jobs');
        show_admin_field('num_jobs_allowed');
    }
}


function add_refresh_btn() {
    var field = $('#id_existing_user');
    field.parent().addClass('input-append');

    var field_width = field.width() - 28;
    field.css("width", String(field_width)+"px");

    field.after('<span class="btn add-on refresh"><i class="icon icon-refresh">');
}


function validate_company_user(e) {
    if (e.target == $('#id_existing_user').get(0)) {
        if (this.timer) {
            clearTimeout(this.timer);
        }

        var pause_interval = 1000;

        if($(window).width() < 500){
            pause_interval = 3000;
        }

        this.timer = setTimeout(function() {validate();}, pause_interval);
    }
    else {
        validate();
    }
}


function validate() {
    var user_email = $('#id_existing_user').val();
    validation_status('validating...')
    $.ajax({
        type: "GET",
        url: "/postajob/companyuser/",
        data: {email: user_email},
        success: function(data) {
            var json = jQuery.parseJSON(data);
            if (json) {
                validation_status('Valid Email');
            }
            else {
                validation_status('Invalid Email');
            }
        }
    });
}


function validation_status(status) {
    var label_text;

    if (status == 'Valid Email') {
        label_text = 'label-success';
    }
    else {
        label_text = 'label-important';
    }

    if ($('#validated').length) {
        $('#validated').removeClass('label-success');
        $('#validated').removeClass('label-important');
        $('#validated').addClass(label_text);
        $('#validated').text(status);
    }
    else {
        $('[class~=refresh]').after('<div id="validated" class="companyuser-validation-label label ' + label_text + '">' + status + '</div>');
    }
}