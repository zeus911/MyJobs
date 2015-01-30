$(document).ready(function() {
    $('tr[id^=message]').click(function(e) {
        // Individual message ids are formatted "message-<id>"
        var message_id = $(e.target).closest('tr').attr('id'),
            modal_selector = '#' + message_id + '-full';
        console.log(modal_selector);
        $(modal_selector).modal();
    });
});
