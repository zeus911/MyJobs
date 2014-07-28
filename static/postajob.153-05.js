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

    // Fake headers on OfflinePurchase Form
    var header_html = '<div class="clear"></div><div class="span3 form-label pull-left initial header"><b>Product</b></div><div class="profile-form-input header"><b>Quantity</b></div>';
    $(header_html).insertAfter('.purchasing-company-field');

    //PurchasedProduct admin, Partner Microsite admin overview
    $('[id^="resend-invoice"]').on("click", function(e) {
        var id_array = $(this).attr('id').split("-")
        resend_invoice(id_array[id_array.length - 1]);
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

function resend_invoice(id) {
    $.ajax({
        type: 'POST',
        url: '/postajob/admin/invoice/' + id + '/'
    });
}
