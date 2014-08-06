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

var fields = ['input[id$=-city]',
    'input[id$=-state]',
    'input[id$=-country]'];

function add_location(location) {
    var html_str = '<div><span>city, region_short country</span><a class="btn pull-right" href="?" id="remove-location-loc_num">Remove</a></div>';
    var location_map = {
        city: location.find('input[id$=-city]').val(),
        region_short: location.find('input[id$=-state]').val(),
        country: location.find('input[id$=-country]').val()
    };
    var location_number = location.find('input[id$=-id]').val();
    if (location_number) {
        location_map['loc_num'] = location_number;
    } else {
        location_map['loc_num'] = form_count;
    }
    html_str = html_str.replace(/city|region_short|country|loc_num/gi,
        function(matched) {
            return location_map[matched];
        });
    $('#job-location-display').append(html_str);
}

function add_locations() {
    $('.formset-form').each(function() {
        add_location($(this));
    });
}

function copy_forms(from, to) {
    var valid = true;
    fields.every(function(element, index, array) {
        var old = from.find(element).val();
        if (old) {
            to.find(element).val(old);
            return true;
        } else {
            return false;
        }
    });
    if (valid) {
        $('#job-location-forms').append(to);
    }
    return valid;
}

function clear_form(form) {
    fields.forEach(function(element, index, array) {
        form.find(element).val('');
    });
}

function create_location_events() {
    $('#add-location').click(function(e) {
        e.preventDefault();
        var new_form = form.replace(/__prefix__/g, form_count);
        new_form = $(new_form);
        var old_form = $('#empty-form');
        var valid = copy_forms(old_form, new_form);
        if (valid) {
            add_location(old_form);
            clear_form(old_form);
            form_count++;
            $('input[id$=-TOTAL_FORMS]').val(form_count);
        }
    });
}