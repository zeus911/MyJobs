$(function() {
    var EditRecordView = Backbone.View.extend({
        el: 'body',

        initialize: function() {
            this.once('renderEvent', function() {
                disable_fields();
                $('[id$=notes]').placeholder();
            });
        },

        render: function() {
            this.trigger('renderEvent');
        },

        events: {
            'click [id$="_search"]': 'save_form',
            'change [id$="_contact_type"]': 'show_fields',
            'change [id$="id_contact"]': 'fill_contact_info'
        },


        save_form: function(e, options) {
            e.preventDefault();

            var form = $('#contact-record-form');

            var data = form.serialize();
            data = data.replace('=on','=True').replace('=off','=False');
            data = data.replace('undefined', 'None');
            $.ajax({
                data: data,
                type: 'POST',
                url: '/saved-search/view/save/',
                success: function(data) {
                    if (data == '') {
                        window.location = '/saved-search/view/';
                    } else {
                        add_errors(data);
                    }
                }
            });
        },

        show_fields: function(){
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
                $('[id$="length"]').show();
                $('label[for$="length"]').show();
            }
        },

        fill_contact_info: function() {
            var form = $('#contact-record-form');

            var data = form.serialize();
            $.ajax({
                data: data,
                type: 'POST',
                url: '/prm/view/records/contact_info',
                success: function(data) {
                    console.log(data);
                    if (data != "") {
                    } else {

                    }
                }
            })
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
    $('[id$="length"]').hide();
    $('label[for$="length"]').hide();
}
