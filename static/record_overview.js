var months = ["None", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

jQuery(document).ready(function($) {
      $(".clickableRow").click(function() {
            window.document.location = $(this).attr("href");
      });
});

$(function() {
    $( ".datepicker" ).datepicker();

    $(document).on("change", '#record_contact', function(){
        update_records(false);
    });
    $(document).on("change", '#record_contact_type', function(){
        update_records(false);
    });

    $('.date-range-submit').click(function(e) {
        e.preventDefault();
        e.stopPropagation();
        update_records(false);
    });
    $('#today').click(function(e) {
        e.preventDefault();
        e.stopPropagation();
        update_records('1');
    });
    $('#thirty-days').click(function(e) {
        e.preventDefault();
        e.stopPropagation();
        update_records('30');
    });
    $('#ninety-days').click(function(e) {
        e.preventDefault();
        e.stopPropagation();
        update_records('90');
    });
});

function update_records(btn_val) {
    var contact = $('#record_contact').val();
    var contact_type = $('#record_contact_type').val();
    var data = "contact=" + contact + "&record_type=" + contact_type + "&company=" + company + "&partner=" + partner;
    if(!btn_val) {
        month_start = $('[name="date-start-chooser_0"]').val();
        day_start = $('[name="date-start-chooser_1"]').val();
        year_start = $('[name="date-start-chooser_2"]').val();
        date_start =  months.indexOf(month_start) + "/" + day_start + "/" + year_start;

        month_end = $('[name="date-end-chooser_0"]').val();
        day_end = $('[name="date-end-chooser_1"]').val();
        year_end = $('[name="date-end-chooser_2"]').val();
        date_end = months.indexOf(month_end) + "/" + day_end + "/" + year_end;

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
            update_time(json);
            update_url(contact, contact_type, date_start, date_end);
        }
    });
}

function update_url(contact, contact_type, date_start, date_end) {
    base_url = $(".records-csv-export-link").attr("href").split("?")[0];
    var query_string = '?company=' + company + '&partner=' + partner + '&';
    if(contact != 'all') {
        query_string += 'contact=' + contact + '&';
    }
    if(contact_type != 'all') {
        query_string += 'record_type=' + contact_type + '&';
    }
    query_string += 'date_start=' + date_start + '&date_end=' + date_end;

    url = base_url + query_string;
    console.log(url);
    $(".records-csv-export-link").attr("href", url);
    $(".records-xml-export-link").attr("href", url + "&file_format=xml");
    $(".records-printer-friendly-export-link").attr("href", url + "&file_format=printer_friendly");
}

function update_time(data) {
    $('.date-range-description').text(data['date_str']);
    if(data['month_start'] != 'None' && data['day_start'] != 'None' && data['year_start'] != 'None') {
        $('[name="date-start-chooser_0"]').val(months[parseInt(data['month_start'])]);
        $('[name="date-start-chooser_1"]').val(data['day_start']);
        $('[name="date-start-chooser_2"]').val(data['year_start']);
    }
    if(data['month_end'] != 'None' && data['day_end'] != 'None' && data['year_end'] != 'None') {
        $('[name="date-end-chooser_0"]').val(months[parseInt(data['month_end'])]);
        $('[name="date-end-chooser_1"]').val(data['day_end']);
        $('[name="date-end-chooser_2"]').val(data['year_end']);
    }
}