$(function() {
    $( ".datepicker" ).datepicker();

});

$(document).ready(function() {
    var date_start = $('input[name=date_start]').attr('placeholder');
    var date_end = $('input[name=date_end]').attr('placeholder');
    console.log(date_start);
    console.log(date_end);
    $("#date_activity").click(function () {
        $(".date_range").toggle();
    });

    $('[class*=details-heading]').click(function(){
        var icon = $(this).children('a').children('span').children('i');
        var item = $(this).next();
        item.collapse().on('shown',function(){
            icon.removeClass('icon-plus');
            icon.addClass('icon-minus');
        }).on('hidden',function(){
            icon.removeClass('icon-minus');
            icon.addClass('icon-plus');
        });
    });

    var _href = $("a.endless_more").attr("href");
    if (_href.length < 100) {
        $("a.endless_more").attr("href", _href + '&date_end=' + date_end + '&date_start=' + date_start);
    }
});