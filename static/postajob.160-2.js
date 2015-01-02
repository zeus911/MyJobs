if(typeof jQuery == 'undefined') {
    var script = document.createElement('script');
    script.type = "text/javascript";
    script.src = "//d2e48ltfsb5exy.cloudfront.net/framework/v2/secure/js/code/jquery-1.7.1.min.js";
    document.getElementsByTagName('head')[0].appendChild(script);
}

var load_event = function(){
    /* intentionally global variables used for the job form*/
    apply_link = $('#id_apply_link').val();
    apply_email = $('#id_apply_email').val();
    apply_info = $('#id_apply_info').val();

    /* don't mistake apply links for emails and vice versa */
    if(apply_link && apply_link.indexOf('mailto:') == 0){
        apply_link = '';
        $('#id_apply_link').val('');
    } else {
        apply_email = '';
        $('#id_apply_email').val('');
    }

    update_apply_fields();
    update_site_fields();
    update_job_limit_fields();
    update_state_selection($('select[id$="__prefix__-country"]').val());

    if($(".product-card").length > 1)
        $("#no-locations").remove();

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
    $(document).on("change", 'select[id$="-country"]', function () {
        update_state_selection($(this).val());
    });

    // Product Form
    $(document).on("change", '#id_job_limit_0', function() {
        update_job_limit_fields();
    });
    $(document).on("change", '#id_job_limit_1', function() {
        update_job_limit_fields();
    });

    //PurchasedProduct admin, Partner Microsite admin overview
    $('[id^="resend-invoice"]').on("click", function(e) {
        var id_array = $(this).attr('id').split("-");
        resend_invoice(id_array[id_array.length - 1]);
    });

    $.each(["#deny-reason", "#block-reason"], function(index, value) {
        $(value).on("keyup", function() {
            var next_button = $(value + "~button");
            if ($(this).val() == "") {
                next_button.attr("disabled", "disabled");
            } else {
                next_button.removeAttr("disabled");
            }
        });
    });
};

if(window.addEventListener) {
    window.addEventListener('load', load_event, false);
} else if (window.attachEvent) {
    // becaue IE is awesome
    window.attachEvent('onload', load_event);
}


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
        $('#id_apply_link').val(apply_link);
        show_field('apply-link');
        show_admin_field('apply_link');

        apply_email = $('#id_apply_email').val() || apply_email;
        apply_info = $('#id_apply_info').val() || apply_info;
        clear_input('apply_email');
        clear_input('apply_info');

        hide_admin_field('apply_email');
        hide_admin_field('apply_info');
        hide_field('apply-email');
        hide_field('apply-instructions');
    }
    else if($('#id_apply_type_1').is(':checked')) {
        $('#id_apply_email').val(apply_email);
        show_field('apply-email');
        show_admin_field('apply_email');

        apply_info = $('#id_apply_info').val() || apply_info;
        apply_link = $('#id_apply_link').val() || apply_link;
        clear_input('apply_info');
        clear_input('apply_link');

        hide_admin_field('apply_link');
        hide_admin_field('apply_info');
        hide_field('apply-link');
        hide_field('apply-instructions');
    }
    else {
        $('#id_apply_info').val(apply_info);
        show_field('apply-instructions');
        show_admin_field('apply_info');

        apply_email = $('#id_apply_email').val() || apply_email;
        apply_link = $('#id_apply_link').val() || apply_link;
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
    'select[id$=-country]'];

function add_location(location) {
    /*
     Creates condensed location tags for a given location.
     */

    var country = location.find('select[id$=-country]').val(),
        region;
    if (country == 'United States' || country == 'Canada') {
        region = location.find('select[id$=-state]').val();
    }
    else {
        region = location.find('input[id$=-region]').val();
    }
    // All added locations will follow the same template, with the city,
    // region, country, and loc_num placeholders replaced with the actual values
    // for the relevant location
    var location_tag = '<div class="product-card no-highlight">city, region country<a id="remove-locations-loc_num" class="pull-right" href="?">Remove</a></div>',
        location_map = {
            city: location.find('input[id$=-city]').val(),
            region: region,
            country: country
        },
    // We need to find out which form on the page is for this location. The
    // form input ids have the structure id_form-#-field, so we can get the
    // form number by grabbing an input and splitting the number from its id.
        field_id = location.find('input[id$=-id]').attr('id'),
        display_container = $('#job-location-display');
    location_map['loc_num'] = field_id.split('-')[1];
    location_tag = location_tag.replace(/city|region|country|loc_num/gi,
        function(matched) {
            return location_map[matched];
        });
    location_tag = $(location_tag);
    display_container.append(location_tag);
}

function add_locations() {
    /*
    Creates location tags for all locations previously added to this job.
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
    fields.forEach(function(element) {
        var from_input = from.find(element),
            from_value = from_input.val();
        if (from_value) {
            to.find(element).val(from_value);
            if (from_input.parents('.required').length > 0) {
                from_input.parent().unwrap();
            }
        } else {
            if (from_input.parents('.required').length == 0) {
                from_input.parent('.profile-form-input').wrap('<div class="required">');
            }
            valid = false;
        }
    });


    if (valid) {
        /*
            country: currently-selected country
            element: selector for the relevant region input
            from_input: Result of selecting element
            from_value: value in from_input
         */
        var country = from.find('select[id$=-country]').val(),
            element, from_input, from_value;
        if (country === 'United States' || country === 'Canada') {
            // My.jobs currently supports region selects for the US and Canada.
            // The options for these two sets of regions reside in the same
            // select, named as follows.
            element = 'select[id$=-state]';
            from_input = from.find(element);
            from_value = from_input.val();
            if (from_value) {
                to.find(element).val(from_value);
                if (from_input.parents('.required').length > 0) {
                    from_input.parent().unwrap();
                }
            } else {
                if (from_input.parents('.required').length == 0) {
                    from_input.parent('.profile-form-input').wrap('<div class="required">');
                }
                valid = false;
            }
        }
        else {
            // The selected country isn't the US or Canada. Use the open-ended
            // input for regions.
            element = 'input[id$=-region]';
            from_input = from.find(element);
            from_value = from_input.val();
            if (from_value) {
                to.find(element).val(from_value);
                if (from_input.parents('.required').length > 0) {
                    from_input.parent().unwrap();
                }
            } else {
                if (from_input.parents('.required').length == 0) {
                    from_input.parent('.profile-form-input').wrap('<div class="required">');
                }
                valid = false;
            }
        }
    }

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
    fields.forEach(function(element) {
        form.find(element).val('');
    });
    form.find('#id_form-__prefix__-region').val('');
    form.find('input[name$=-zipcode]').val('');
}

function create_location_events() {
    /*
    Creating and editing jobs requires two events to be set up for locations to
    function properly, one each for the add and remove buttons.
     */
    $('[name$=-DELETE]').each(function() {
        // The delete input added by formsets seems to default to checked.
        $(this).removeAttr('checked');
    });
    $('#add-location').click(function(e) {
        /*
        Validates location form, copies valid forms to the correct location,
        and adds a display for added locations.
         */
        e.preventDefault();

        // remove the card that appears when no locations are present
        $("#no-locations").remove();
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
    $('#job-location-display').on('click', 'a', function(e) {
        /*
         Toggles the delete input for a given location. Changes the text of the
         remove button to either Remove or Re-add based on the input status.
         */
        e.preventDefault();
        var id = $(this).attr('id').split('-')[2],
            delete_input = $('input[name=form-' + id + '-DELETE]'),
            checked = delete_input.attr('checked') == 'checked';
        if (checked) {
            delete_input.removeAttr('checked');
            $(this).parent('.product-card').css('text-decoration', 'none');
            $(this).text('Remove');
        } else {
            delete_input.attr('checked', 'checked');
            $(this).parent('.product-card').css('text-decoration',
                                                'line-through');
            $(this).text('Re-add');
        }
    });
}

function expand_errors(contents) {
    /*
     Expands the content portion of an accordion (denoted by the :contents:
     param) if an input inside the accordion has errors (has 'required' as
     one of its classes)
     */
    $('.required').each(function() {
        var parent_accordion = $(this).parents(contents);
        if (parent_accordion.css('display') == "none") {
            parent_accordion.slideToggle();
        }
    });
}

function update_state_selection(country) {
    /*
        region: open-ended input
        state: select box for US/Canadian states, provinces, and territories
     */
    var region = $('#id_form-__prefix__-region'),
        state = $('#id_form-__prefix__-state');
    if (country == 'United States' || country == 'Canada') {
        region.hide();
        $('label[for="id_form-__prefix__-region"]').hide();

        state.show();
        $('label[for="id_form-__prefix__-state"]').show();

        country = country.replace(' ', '.');
        var hidden = $('#hidden-options'),
            this_country = hidden.find('option.' + country),
            other_country = state.find('option:not(.' + country + ')');
        this_country.appendTo(state);
        other_country.appendTo(hidden);
        state.val(state.find('option:first_of_type').val());
    }
    else {
        region.show();
        $('label[for="id_form-__prefix__-region"]').show();

        state.hide();
        $('label[for="id_form-__prefix__-state"]').hide();
    }
}
