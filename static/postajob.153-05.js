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

// Required fields for locations
// This is also verified server-side; checking in JS just cuts down on the
// number of requests we have to do.
var fields = ['input[id$=-city]',
    'input[id$=-state]',
    'input[id$=-country]'];

function add_location(location) {
    /*
    Creates condensed location tags for this job's locations
     */
    var html_str = '<div><span>city, region_short country</span><a class="pull-right" href="?" id="remove-location-loc_num">Remove</a></div>';
    var location_map = {
        city: location.find('input[id$=-city]').val(),
        region_short: location.find('input[id$=-state]').val(),
        country: location.find('input[id$=-country]').val()
    };
    // We need to find out which form on the page is for this location. The form
    // input ids have the structure id_form-#-field, so we can get the form
    // number by grabbing an input and splitting the number from its id.
    var field_id = location.find('input[id$=-id]').attr('id');
    location_map['loc_num'] = field_id.split('-')[1];
    html_str = html_str.replace(/city|region_short|country|loc_num/gi,
        function(matched) {
            return location_map[matched];
        });
    $('#job-location-display').append(html_str);
}

function add_locations() {
    /*
    Adds location tags for all locations previously added to this job.
     */
    $('.formset-form').each(function() {
        add_location($(this));
    });
}

function copy_forms(from, to) {
    /*
    Copy input values from the formset's default empty form to a more permanent
    form.
     */
    var valid = true;
    fields.forEach(function(element, index, array) {
        var old = from.find(element).val();
        if (old) {
            to.find(element).val(old);
        } else {
            valid = false;
        }
    });
    if (valid) {
        // Zip codes are optional and shouldn't affect the validity of a
        // location. If the form is valid, copy the zip code from it as well.
        var zip_selector = 'input[name$=-zipcode]';
        to.find(zip_selector).val(from.find(zip_selector).val());

        // Delete checkboxes for locations seem to start out as checked; they
        // shouldn't be.
        to.find('[name$=-DELETE]').removeAttr('checked');
        $('#job-location-forms').append(to);
    }
    return valid;
}

function clear_form(form) {
    /*
    Clears all values from our input form so that further locations can be
    added.
     */
    fields.forEach(function(element, index, array) {
        form.find(element).val('');
    });
    form.find('input[name$=-zipcode]').val('');
}

function create_location_events() {
    /*
    Creating and editing jobs requires two events to be set up for locations to
    function properly, one each for the add and remove buttons.
     */
    $('[name$=-DELETE]').each(function() {
        $(this).removeAttr('checked');
    });
    $('#add-location').click(function(e) {
        e.preventDefault();
        // form_count holds the current number of location forms on the page.
        // The form numbers start at 0, so form_count also represents the next
        // available form number.

        // form holds the formset's empty form with __prefix__ in place of the
        // form number. We can turn this into a functional form by replacing
        // the prefix with the next available number.
        var new_form = form.replace(/__prefix__/g, form_count);
        new_form = $(new_form).wrap('<div class="formset-form">');
        var old_form = $('#empty-form');
        var valid = copy_forms(old_form, new_form);
        if (valid) {
            add_location(new_form);
            clear_form(old_form);
            $('input[name$=-' + form_count + '-DELETE').removeAttr('checked');
            // The new location has been added; increment the number of forms
            // and update the TOTAL_FORMS input.
            form_count++;
            $('input[id$=-TOTAL_FORMS]').val(form_count);
        }
    });
    $('a[id^=remove-location-]').click(function(e) {
        e.preventDefault();
        var id = $(this).attr('id').split('-')[2];
        $('input[name=form-' + id + '-DELETE]').attr('checked', 'checked');
        // TODO: Remove this and turn the delete button into a toggle
        $(this).parent().remove();
    });
}