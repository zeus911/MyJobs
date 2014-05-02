var ss_username = "directseo@directemployersfoundation.org";
var ss_api_key = "6fcd589a4efa72de876edfff7ebf508bedd0ba3e";
var ss_api_str = "&username=" + ss_username  + "&api_key=" + ss_api_key;
var base_url = 'https://secure.my.jobs';
var ss_url = window.location.href;
var most_recent_html = '';

$(document).ready(function(){
    get_default_widget_html(false);
});

function handle_error() {
    // Fills with the most recent text and then overwrites applicable parts
    // with the error message. Uses the most recent text to ensure formatting
    // and variables supplied by myjobs are persistent, so the experience
    // for logged in users continues to be the same.

    fill(most_recent_html);
    $('.saved-search-form').prepend('<em class="warning">Something went wrong!</em>');
    $('.saved-search-form > form > b').html('<p>Your search could not successfully be created.</p>');
    $('label[for="saved-search-email"]').html('<p>Your search could not successfully be created.</p>');
    $('.saved-search-button').html('Try saving this search again');
}

function fill(html) {
    $('#de-myjobs-widget').html(html);
    most_recent_html = html;
}

function save_search() {
    // If there is any hint that there isn't a well-defined user email
    // provided, attempts to get a user from the input and create a new user.
    // Otherwise, uses the currently provided user to create a saved search.

    if (user_email != 'None' && user_email != 'undefined' && user_email) {
        $('.saved-search-form').html('<em class="loading">Saving this search</em>');
        create_saved_search();
    }
    else {
        try {
            user_email = $('#saved-search-email').val();
            $('.saved-search-form').html('<em class="loading">Saving this search</em>');
            create_user();
        }
        catch(err) {
            handle_error();
        }
    }
}

function reload_default_widget(data) {
    if(data.error) {
        handle_error();
    }
    else {
        get_default_widget_html(true);
    }
}

function get_default_widget_html(success) {
    if(success) {
        ajax_url = base_url + '/saved-search/widget/?callback=fill&success=' + user_email + '&url=' + ss_url;
    }
    else {
        ajax_url = base_url + '/saved-search/widget/?callback=fill&url=' + ss_url;
    }
    jsonp_ajax_call(ajax_url);
}


function create_saved_search() {
    jsonp_ajax_call(base_url + "/api/v1/savedsearch/?callback=reload_default_widget&email=" + user_email + ss_api_str + "&url=" + ss_url);
}

function create_user() {
    jsonp_ajax_call(base_url + "/api/v1/user/?callback=create_saved_search&email=" + user_email + ss_api_str);
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