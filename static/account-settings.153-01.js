$(document).ready(function() {
    var hash = window.location.hash;

    $("[class*='as-section']").children('h4').each(function() {
        $(this).on("click", function() {
            closeOtherSections();
            var parent = $(this).parent();
            if($(this).siblings('div').is(':visible')){
                parent.addClass('as-hide');
            } else {
                parent.removeClass('as-hide');
            }
        });
    });

    if(hash) {
        closeOtherSections();
        $("div"+ hash + "").children('h4').trigger("click");
    }

    $("[class*='confirm-modal']").each(function() {
        $(this).one("hover", function(e) {
            $.ajax({
                global: false,
                url: static_url + "bootstrap/bootstrap-modalmanager.js",
                dataType: "script",
                cache: true
            });
            $.ajax({
                global: false,
                url: static_url + "bootstrap/bootstrap-modal.js",
                dataType: "script",
                cache: true
            });
        });
        $(this).on("click", function(e) {
            e.preventDefault();
            $("#captcha_modal").modal();
        });
    });

    $("#to-disable").on("click", function(){
        $(this).parent("div")
    })
});

function closeOtherSections() {
    $("[class*='as-section']").each(function () {
        if($(this).children('div').is(':visible')) {
            $(this).addClass('as-hide');
        }
    });
}
