$(document).ready(function() {
    var hash = window.location.hash;

    $(".as-section").on("click", function() {
        var closest_content = $(this).next();
        $(closest_content).slideToggle();
    });

    if(hash) {
        closeOtherSections();
        $("div"+ hash + "").trigger("click");
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
        $("#as-delete").trigger("click");
        $('#as-disable').trigger("click");
    })
});

function closeOtherSections() {
    $("[class*='as-section']").each(function () {
        if($(this).next().is(':visible')) {
            $(this).next().hide();
        }
    });
}
