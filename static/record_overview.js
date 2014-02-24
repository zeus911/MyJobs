jQuery(document).ready(function($) {
      $(".clickableRow").click(function() {
            window.document.location = $(this).attr("href");
      });
});

$(function() {
    $(document).on("change", '#record_contact', function(){
        update_records(this);
    });
    $(document).on("change", '#record_contact_type', function(){
        update_records(this);
    });
});

function update_records() {
    var contact = $('#record_contact').val();
    var contact_type = $('#record_contact_type').val();
    var data = "contact=" + contact + "&contact_type=" + contact_type + "&company=" + company + "&partner=" + partner;

    $.ajax({
        data: data,
        type: 'GET',
        url: '/prm/view/records/update',
        success: function(data) {
            $('#record-results').replaceWith(data);
        }
    });

}