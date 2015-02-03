$(document).ready(function() {
    $('tr[id^=message]').click(function(e) {
        // Individual message ids are formatted "message-<id>"
        var target = $(e.target);
        if (!target.is('a')) {
            // We don't want to open a modal if the user is clicking on an
            // anchor that happens to be in this row (delete, mark read).
            var message_id = target.closest('tr').attr('id'),
                modal_selector = '#' + message_id + '-full';
            $(modal_selector).modal();
            on_read(target);
        }
    });

    $('[class*=mymessage-delete-]').click(function(){
        delete_message(this);
    });
});

function on_read(clicked) {
    var parent = clicked.parents('tr');
    // On future views, this is all done at the template level; As this
    // was initiated by ajax, that doesn't happen.
    if (clicked.is('a[class*=mymessage-read]')) {
        clicked.hide();
    } else {
        var button = parent.find('a[class*=mymessage-read]');
        readMessage(button);
        button.hide();
    }
    parent.addClass('read');
}

function delete_message(button) {
    var message_box = $(button),
        name = message_box.attr('class').split(' ').pop(),
        data = "name="+name;
    $.ajax({
        type: 'GET',
        url: '/message/delete/',
        data: data,
        dataType: 'json',
        success: function(data) {
            $('#messages').replaceWith(data);
        }
    });
}
