$(document).ready(function() {
    $('tr[id^=message]').click(function(e) {
        // Individual message ids are formatted "message-<id>"
        var target = $(e.target);
        if (!target.is('a')) {
            // We don't want to open a modal if the user is clicking on an
            // anchor that happens to be in this row.
            var message_id = target.closest('tr').attr('id'),
                modal_selector = '#' + message_id + '-full';
            $(modal_selector).modal();
        }
    });
});

var on_read = function(clicked) {
    // On future views, this occurs during template processing; As this was
    // initiated by ajax, that doesn't happen.
    clicked.hide();
    clicked.parents('tr').addClass('read');
};
