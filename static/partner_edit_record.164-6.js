$(document).ready(function() {
    $("#p-tags").hide();
    $("#p-tags").tagit({
        allowSpaces: true,
        tagSource: function(search, showChoices) {
            var value = $(".tagit-new > input").val(),
                search = {value: value},
                that = this;
            $.ajax({
                type: "GET",
                url: "/prm/view/records/get-tags",
                data: search,
                success: function(data) {
                    var jdata = jQuery.parseJSON(data);
                    showChoices(that._subtractArray(jdata, that.assignedTags()))
                }
            });
        },
        beforeTagAdded: function(event, ui) {
            ui.tag.hide();
            var name = ui.tag.children("span").html();
            $.ajax({
                type: "GET",
                url: "/prm/view/records/get-tag-color",
                data: {"name": name},
                success: function(data) {
                    var jdata = jQuery.parseJSON(data);
                    if(jdata.length > 0)
                        ui.tag.css("background-color", "#"+jdata[0]);
                    ui.tag.show();
                }
            })
        },
        autocomplete: {delay: 0, minLength: 1},
        placeholderText: "Add Tag"
    });

    show_fields();
});

$(function() {
    $("[id$='_contact_type']").on("change", function() {
        show_fields();
    });

    $("#id_contact").on("change", function() {
        if($('[id$="id_contact"]').val()) {
            var form = $('#contact-record-form'),
                data = form.serialize();

            $.ajax({
                data: data,
                type: 'POST',
                url: '/prm/view/records/contact_info',
                success: function(data) {
                    json = jQuery.parseJSON(data);
                    if (json.hasOwnProperty('error')) {
                        $('.form-status').html('<div class="alert alert-error"><button type="button" class="close" data-dismiss="alert">&times;</button>'+json['error']+'.</div>');
                    } else {
                        if($('.form-status').html() != '') {
                            $('.form-status').html('');
                        }
                        for(var key in json) {
                            $('[id$="_'+key+'"]').val(json[key]);
                        }

                    }
                }
            })
        } else {
            $('[id$="_email"]').val('');
            $('[id$="_phone"]').val('');
        }
    });

    $(document).on("change", '[id^=id_attachment]', function(){
        add_additional_input(this);
    });
});

function disable_fields(){
    $('[id$="contact_email"]').hide();
    $('label[for$="contact_email"]').hide();
    $('[id$="contact_phone"]').hide();
    $('label[for$="contact_phone"]').hide();
    $('[id$="location"]').hide();
    $('label[for$="location"]').hide();
    display_length_widget('hide');
    $('[id$="job_id"]').hide();
    $('label[for$="job_id"]').hide();
    $('[id$="job_applications"]').hide();
    $('label[for$="job_applications"]').hide();
    $('[id$="job_interviews"]').hide();
    $('label[for$="job_interviews"]').hide();
    $('[id$="job_hires"]').hide();
    $('label[for$="job_hires"]').hide();
    $('[id$="subject"]').hide();
    $('label[for$="subject"]').hide();
    $('label[for*="date_time_"]').hide();
    $(".date-time").hide();
}

function display_length_widget(display){
    if (display == "show"){
        $('[id*="length"]').parent().show();
        $('label[for*="length"]').show();
    }
    if (display == "hide"){
        $('[id*="length"]').parent().hide();
        $('label[for*="length"]').hide();
    }
}

function show_fields(){
    disable_fields();
    var contact_type = $('[id$="contact_type"]').val();
    if(contact_type == 'email'){
        $('[id$="contact_email"]').show();
        $('label[for$="contact_email"]').show();
        $('[id$="subject"]').show();
        $('label[for$="subject"]').show();
        $('label[for*="date_time_"]').show();
        $(".date-time").show();
    } else if(contact_type == 'phone') {
        $('[id$="contact_phone"]').show();
        $('label[for$="contact_phone"]').show();
        $('[id$="length"]').show();
        $('label[for$="length"]').show();
        $('label[for*="date_time_"]').show();
        $(".date-time").show();
        $('[id$="subject"]').show();
        $('label[for$="subject"]').show();
    } else if(contact_type == 'meetingorevent') {
        $('[id$="location"]').show();
        $('label[for$="location"]').show();
        $('label[for*="date_time_"]').show();
        display_length_widget("show");
        $(".date-time").show();
        $('[id$="subject"]').show();
        $('label[for$="subject"]').show();
    } else if(contact_type == 'job'){
        $('[id$="contact_email"]').show();
        $('label[for$="contact_email"]').show();
        $('[id$="job_id"]').show();
        $('label[for$="job_id"]').show();
        $('[id$="job_applications"]').show();
        $('label[for$="job_applications"]').show();
        $('[id$="job_interviews"]').show();
        $('label[for$="job_interviews"]').show();
        $('[id$="job_hires"]').show();
        $('label[for$="job_hires"]').show();
    } else {
        $('[id$="subject"]').show();
        $('label[for$="subject"]').show();
        $('label[for*="date_time_"]').show();
        $(".date-time").show();
    }
}

function add_additional_input(field) {
    if($(field).val() != '') {
        $('[id^=span_attachment]:first').before('<span id="span_attachment_' + $("[id^=id_attachment]").length + '"><input id="id_attachment_' + $("[id^=id_attachment]").length + '" multiple="multiple" name="attachment" type="file"></span>');
    }
    else if(number_of_blank_and_visible_file_inputs() > 1){
        $(field).hide();
    }
}

function number_of_blank_and_visible_file_inputs() {
    var number_that_are_blank_and_visible = 0;
    $("[id^=id_attachment]").each(function() {
        if(($(this).val() == "" || $(this).val() == 0) && $(this).is(":visible")) {
            number_that_are_blank_and_visible += 1;
        }
    });
    return number_that_are_blank_and_visible;
}
