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
    $('#all-days').click(function(e) {
        e.preventDefault();
        e.stopPropagation();
        update_records('0');
    });
});

function update_records(btn_val) {
    var contact = $('#record_contact').val();
    var contact_type = $('#record_contact_type').val();
    var data = "contact=" + contact + "&record_type=" + contact_type + "&company=" + company_id + "&partner=" + partner_id;
    if(admin_id != 'None') {
        data += '&admin=' + admin_id;
    }
    if(!btn_val) {
        date_start =  get_date_start();
        date_end = get_date_end();

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
            if($('#record-download').length) {
                date_start = get_date_start();
                date_end = get_date_end();
                update_url(contact, contact_type, date_start, date_end);
            }
        }
    }).done(function() {
        $("#time-range-menu").trigger("click");
    });
}

function update_url(contact, contact_type, date_start, date_end) {
    base_url = $(".records-csv-export-link").attr("href").split("?")[0];
    var query_string = '?company=' + company_id + '&partner=' + partner_id + '&';
    if(contact != 'all') {
        query_string += 'contact=' + contact + '&';
    }
    if(contact_type != 'all') {
        query_string += 'record_type=' + contact_type + '&';
    }
    query_string += 'date_start=' + date_start + '&date_end=' + date_end;

    url = base_url + query_string;
    $(".records-csv-export-link").attr("href", url);
    $(".records-excel-export-link").attr("href", url + "&file_format=xls");
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

function get_date_start() {
    month_start = $('[name="date-start-chooser_0"]').val();
    day_start = $('[name="date-start-chooser_1"]').val();
    year_start = $('[name="date-start-chooser_2"]').val();
    return months.indexOf(month_start) + "/" + day_start + "/" + year_start;
}

function get_date_end() {
    month_end = $('[name="date-end-chooser_0"]').val();
    day_end = $('[name="date-end-chooser_1"]').val();
    year_end = $('[name="date-end-chooser_2"]').val();
    return months.indexOf(month_end) + "/" + day_end + "/" + year_end;
}