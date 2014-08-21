$(document).ready(function() {
    $('[id$=master-filter-btn]').click(function(e) {
        e.preventDefault();
        var field = (this.id).replace('-master-filter-btn', '');
        request_filter = $("#" + field + "-master-filter").val();

        $("[id$=" + field + "_from]").find('option').remove();
        $("#" + field + "-master-filter").val('');
        // For some reason without this the _to box doesn't adjust
        // to the right height automatically.
        $("#id_" + field + "_to").css("height", "218px");
        
        
        // Updates the contents of the _from select box with the filtered
        // values, and re-init the arrays storing the values.
        update = function(data) {
            $.each(data, function(key, value){
                option = '<option value="' + key + '">' 
                        + key + " : " + value + '</option>';
                $('#id_' + field + '_from').append(option);
            });
        SelectBox.init('id_' + field + '_from');
        SelectBox.init('id_' + field + '_to');
        };

        // Gets jsonp response containing buid, buid title (key, value) pairs.
        // Response is handled by callback function update().
        $.ajax({
            url: "/data/buids?"
               + "filter=" + request_filter,
            dataType: "jsonp",
            jsonpCallback: "update",
            type: "GET",
            crossDomain: true,
            headers: {
                'Content-Type': "application/json", 
                Accept: 'text/javascript'
            },            
        });                    
    });
});
