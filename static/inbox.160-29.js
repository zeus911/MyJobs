$(document).ready(function() {
    $(document).on('click', 'tr[id^=message]', function(e) {
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

    $(document).on('click', '[class*=mymessage-delete-]', function(){
        delete_message(this);
    });

    if (typeof(clicked) != 'undefined') {
        // A message was clicked in the topbar; ensure its modal opens.
        var message = $('#message-' + clicked);
        message.click();
    }
});

function on_read(clicked) {
    var parent = clicked.is('tr') ? clicked : clicked.parents('tr');
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
        url: '/message/delete/' + window.location.search,
        data: data,
        dataType: 'json',
        success: function(data) {
            $('#messages').html(data);
        }
    });
}
