if(typeof jQuery == "undefined") {
    var script = document.createElement('script');
    script.type = "text/javascript";
    script.src = "//d2e48ltfsb5exy.cloudfront.net/framework/v2/js/code/jquery-1.7.1.js";
    document.getElementsByTagName('head')[0].appendChild(script);
}

window.onload = function() {
    $.ajax({
        type: 'GET',
        url: '/ajax/filtercarousel/',
        success: function(data) {
            add_filter(jQuery.parseJSON(data));
        }
    }).done(function() {
        if (typeof Pager == "undefined") {
            $.getScript("//d2e48ltfsb5exy.cloudfront.net/content_ms/files/pager.163-24.js");
        }
    });
};

function add_filter(data) {
    $(".direct-ajax-filter-carousel").html(data);
}