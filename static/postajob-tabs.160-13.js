$(document).ready(function() {
    $(".card-tabs li").on("click", function() {
        $(".card-tabs li").removeClass("active");
        $(this).addClass("active");
        var clicked = $(this).attr("id").split("-")[0];
        $(".card-wrapper").css("display", "none");
        $("div[id*='"+clicked+"-']").css("display", "block");
    });
});