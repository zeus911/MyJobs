$(function() {
    $( ".datepicker" ).datepicker();

});

$(document).ready(function() {
    var field = $('#search-field');
    var addon = field.next();

    var field_width = field.outerWidth() - addon.outerWidth();
    field.css("width", String(field_width)+"px");

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
    if(_href){
        if (_href.length < 100) {
            $("a.endless_more").attr("href", _href + '&date_end=' + date_end + '&date_start=' + date_start);
        }
    }
});