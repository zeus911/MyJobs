$(function() {
    var EditRecordView = Backbone.View.extend({
        el: 'body',

        initialize: function() {
            this.once('renderEvent', function() {
                show_fields();
                add_datepicker();
                $('[id$=notes]').placeholder();
            });
        },

        render: function() {
            this.trigger('renderEvent');
        },

        events: {
            'click [id$="_record_save"]': 'save_form',
            'change [id$="_contact_type"]': 'showing_fields',
            'change [id$="id_contact_name"]': 'fill_contact_info'
        },


        save_form: function(e, options) {
            e.preventDefault();

            var form = $('#contact-record-form');

            var company_id = $('[name=company]').val();
            var partner_id = $('[name=partner]').val();

            var data = form.serialize();
            data = data.replace('=on','=True').replace('=off','=False');
            data = data.replace('undefined', 'None');
            $.ajax({
                data: data,
                type: 'POST',
                url: '/prm/view/records/edit',
                success: function(data) {
                    if (data == '') {
                        window.location = '/prm/view/records?company='+company_id+'&partner='+partner_id;
                    } else {
                        console.log(data);
                        var json = jQuery.parseJSON(data);

                        // remove color from labels of current errors
                        $('[class*=required]').parent().prev().removeClass('error-text');

                        // remove current errors
                        $('[class*=required]').children().unwrap();

                        if($.browser.msie){
                            $('[class*=msieError]').remove()
                        }

                        for (var index in json) {
                            var $error = $('[id$="_'+index+'"]');
                            if(!$error[0]){
                                $error = $('[id*="_'+index+'"]');
                            }
                            if($error.length > 1){
                                for(var i=0; i < $error.length; i++){
                                    if(i==0){
                                        var $labelOfError = $error.parent().prev();
                                        $labelOfError.addClass('error-text');
                                    }
                                    $($error[i]).wrap('<div class="required" />');
                                    $($error[i]).attr("placeholder",json[index][0]);
                                    $($error[i]).val('')
                                }
                            }else{
                                var $labelOfError = $error.parent().prev();

                                // insert new errors after the relevant inputs
                                $error.wrap('<div class="required" />');
                                $error.attr("placeholder",json[index][0]);
                                $error.val('')
                                $labelOfError.addClass('error-text');
                            }
                        }
                    }
                }
            });
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
    } else if(contact_type == 'phone') {
        $('[id$="contact_phone"]').show();
        $('label[for$="contact_phone"]').show();
        $('[id$="length"]').show();
        $('label[for$="length"]').show();
    } else if(contact_type == 'facetoface') {
        $('[id$="location"]').show();
        $('label[for$="location"]').show();
        display_length_widget("show");
    }
}

function add_datepicker(){
    var date = $("input[id$='date_time_0']");
    date.datepicker({dateFormat: window.dateFormat, constrainInput: false});
    if($(window).width() <= 501){
        var window_width = $(window).width();
        var field_width = window_width - 81;
        date.css({"width": String(field_width)+"px", "display": "inline-block", "margin-right": "5px"});
        $('[id*="id_date_time_"]').slice(1).each(function() {
            $(this).css("width", field_width/3+"px");
        });
        date.after('<span class="btn add-on calendar"><i class="icon-search icon-calendar"></i></span>');
    }
}