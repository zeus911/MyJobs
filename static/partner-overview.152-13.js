$(document).ready(function() {
    var rows = find_rows();
    add_data_attr(rows);
    var max_num = get_max(rows);
    var current_num;
    if(rows.length > 0) {
        current_num = 1;
    } else {
        current_num = 0;
    }
    change_marker(current_num, max_num);
    show_row(rows, current_num);
    $('#activity-table').show();

    $('#previous').on( "click", function() {previous();} );
    $('#next').on( "click", function() {next();} );
});

function next() {
    var rows = find_rows();
    var max_num = get_max(rows);
    var current_num = find_currently_shown(rows);
    if(current_num == max_num){
        current_num = 1;
    } else {
        current_num = current_num + 1;
    }
    show_row(rows, current_num);
    change_marker(current_num, max_num);
}

function previous() {
    var rows = find_rows();
    var max_num = get_max(rows);
    var current_num = find_currently_shown(rows);
    if(current_num == 1){
        current_num = max_num;
    } else {
        current_num = current_num - 1;
    }
    show_row(rows, current_num);
    change_marker(current_num, max_num);
}

function add_data_attr(rows){
    for(var i=0; i < rows.length; i++){
        $(rows[i]).attr("data-num", i+1);
    }
}

function find_rows(){
    return $('#activity-table').children().children();
}

function get_max(rows){
    return rows.length
}

function change_marker(current_num, max_num){
    $('#activity-num').html(current_num + " of " + max_num);
}

function hide_rows(rows){
    for(var i=0; i < rows.length; i++){
        $(rows[i]).hide();
    }
}

function show_row(rows, current_row){
    hide_rows(rows);
    for(var i=0; i < rows.length; i++){
        if($(rows[i]).data('num') == current_row){
            $(rows[i]).show();
        }
    }
}

function find_currently_shown(rows){
    for(var i=0; i < rows.length; i++){
        if($(rows[i]).is(':visible')){
            var shown = $(rows[i]).data('num');
        }
    }
    return shown
}