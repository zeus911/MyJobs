jQuery(document).ready(function($) {
      $(".clickableRow").click(function() {
            window.document.location = $(this).attr("href");
      });
});

$(function() {
    $( ".datepicker" ).datepicker();

    $("#record_contact").val('all');
    $("#record_contact_type").val('all');

    $(document).on("change", '#record_contact', function(){
        update_records(false);
    });
    $(document).on("change", '#record_contact_type', function(){
        update_records(false);
    });

    $('input[name="date_range_form_submit"]').click(function(e) {
        e.preventDefault();
        e.stopPropagation();
        update_records(false);
    });
    $('input[name="today"]').click(function(e) {
        e.preventDefault();
        e.stopPropagation();
        update_records('today');
    });
    $('input[name="seven_days"]').click(function(e) {
        e.preventDefault();
        e.stopPropagation();
        update_records('seven_days');
    });
    $('input[name="thirty_days"]').click(function(e) {
        e.preventDefault();
        e.stopPropagation();
        update_records('thirty_days');
    });
});

function update_records(btn_val) {
    var contact = $('#record_contact').val();
    var contact_type = $('#record_contact_type').val();
    var data = "contact=" + contact + "&contact_type=" + contact_type + "&company=" + company + "&partner=" + partner;
    if(!btn_val) {
        date_start = $('input[name="date_start"]').val();
        date_end = $('input[name="date_end"]').val();
        if(!date_end) {
            date_end = $('input[name="date_end"]').attr('placeholder');
        }
        if(!date_start) {
            date_start = $('input[name="date_start"]').attr('placeholder');
        }
        data += "&date_start=" + date_start + "&date_end=" + date_end;
    }
    else {
        data += "&date=" + btn_val;
    }

    $.ajax({
        data: data,
        type: 'GET',
        url: '/prm/view/records/update',
        success: function(data) {
            json = jQuery.parseJSON(data);
            $('#record-results').replaceWith(json['html']);
            $(".date-range-select-form").removeClass('date-range-select-form-visible');
            update_time(json['date_str'], json['date_start'], json['date_end']);
        }
    });

}

function update_time(date_str, date_start, date_end) {
    $('.date-range').text(date_str);
    if(date_start != 'None') {
        $('input[name="date_start"]').val(date_start);
    }
    if(date_end != 'None') {
        $('input[name="date_end"]').val(date_end);
    }
}