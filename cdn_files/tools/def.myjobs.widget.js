var ss_username = "directseo@directemployersfoundation.org";
var ss_api_key = "6fcd589a4efa72de876edfff7ebf508bedd0ba3e";
var ss_api_str = "&username=" + ss_username  + "&api_key=" + ss_api_key;
var ss_url = window.location.href;

$(document).ready(function(){
    get_default_widget_html(false);
});

function fill(html) {
    $('#de-myjobs-widget').html(html);
}

function save_search() {
    $('.saved-search-form').html('<<em class="loading">Saving this search</em>');
    if (user_email != 'None') {
        create_saved_search();
    }
    else {
        user_email = $('#saved-search-email').val();
        create_user();
    }
}

function reload_default_widget() {
    get_default_widget_html(true);
}

function get_default_widget_html(success) {
    if(success) {
        ajax_url = 'https://secure.my.jobs/saved-search/widget/?callback=fill&success=' + user_email + '&url=' + ss_url;
    }
    else {
        ajax_url = 'https://secure.my.jobs/saved-search/widget/?callback=fill&url=' + ss_url;
    }
    jsonp_ajax_call(ajax_url);
}


function create_saved_search() {
    jsonp_ajax_call('https://secure.my.jobs' + "/api/v1/savedsearch/?callback=reload_default_widget&email=" + user_email + "&url=" + ss_url + ss_api_str);
}

function create_user() {
    jsonp_ajax_call('https://secure.my.jobs' + "/api/v1/user/?callback=create_saved_search&email=" + user_email + ss_api_str);
}


function jsonp_ajax_call(ajax_url) {
    $.ajax({
        url: ajax_url,
        dataType: "jsonp",
        type: "GET",
        crossDomain: true,
        jsonp: false,
        processData: false,
        headers: {
            'Content-Type': "application/json",
            Accept: 'text/javascript'
        },
    });
}