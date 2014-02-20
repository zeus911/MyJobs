$(function() {
    var EditRecordView = Backbone.View.extend({
        el: 'body',

        initialize: function() {
            this.once('renderEvent', function() {
                show_fields();
                $('[id$=notes]').placeholder();
            });
        },

        render: function() {
            this.trigger('renderEvent');
        },

        events: {
            'change [id$="_contact_type"]': 'showing_fields',
            'change [id$="id_contact_name"]': 'fill_contact_info'
        },

        showing_fields: function(){
            show_fields();
        },

        fill_contact_info: function() {
            if($('[id$="id_contact_name"]').val() != 'None'){
            var form = $('#contact-record-form');

            var data = form.serialize();
                $.ajax({
                    data: data,
                    type: 'POST',
                    url: '/prm/view/records/contact_info',
                    success: function(data) {
                        json = jQuery.parseJSON(data);
                        if (json.hasOwnProperty('error')) {
                            $('.form-status').html('<div class="alert alert-error"><button type="button" class="close" data-dismiss="alert">&times;</button>'+json['error']+'.</div>');
                        } else {
                            if($('.form-status').html() != ''){
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
        }
    });

    var EditRecord = new EditRecordView;
    EditRecord.render();
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
        $('[id*="date_time_"]').show();
        $('label[for*="date_time_"]').show();
    } else if(contact_type == 'phone') {
        $('[id$="contact_phone"]').show();
        $('label[for$="contact_phone"]').show();
        $('[id$="length"]').show();
        $('label[for$="length"]').show();
        $('[id*="date_time_"]').show();
        $('label[for*="date_time_"]').show();
    } else if(contact_type == 'facetoface') {
        $('[id$="location"]').show();
        $('label[for$="location"]').show();
        $('[id*="date_time_"]').show();
        $('label[for*="date_time_"]').show();
        display_length_widget("show");
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

        // Hiding fields
        $('[id$="subject"]').hide();
        $('label[for$="subject"]').hide();
        $('[id*="date_time_"]').hide();
        $('label[for*="date_time_"]').hide();
    }
}