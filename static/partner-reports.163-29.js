$(document).ready(function () {
    page = $('.prm-header').children(':first').html();
    $( ".datepicker" ).datepicker();

    if(page === 'Overview'){
        draw_donut('small');
    }
    if(page === 'Reports'){
        draw_donut('big');
        draw_chart();
    }
    if($(window).width() < 500){
        $('#date-range-list').addClass('mobile-filter-selectlike');
        $('#admin-list').addClass('mobile-filter-selectlike');
        $('#download-list').addClass('mobile-filter-selectlike');
    } else {
        $('#date-range-list').css('margin-left', '-184px');
        $('#admin-list').css('margin-left', '-90px');
        $('#download-list').css('margin-left', '-82px');
    }
});


$(function() {
    $(document).on("click", "#email, #phone, #meetingorevent, #job", function(e) {
        go_to_records(e);
    });

    $(".header-menu").on( "click", function(e) {
        dropdown(e);
    });

    $("#today, #thirty-days, #ninety-days, #all-days").on( "click", function(e) {
        if(page === 'Reports'){
            submit_date_range_from_li(e);
        }
    });

    $("#custom-date-dropdown").on("click", function(e) {
        e.stopPropagation();
    });

    $(".black-mask").on("click", function() {
        if($(window).width() < 500){
            $('.black-mask').hide();
            disable_scroll('false');
            $('[class*=header-menu]').removeClass('show-drop');
        }
    });

    $("#date-drop").on("click", function(e) {
        e.stopPropagation();
        var insidedrop = $('#custom-date-dropdown');
        if(insidedrop.is(":visible")){
            insidedrop.hide();
            insidedrop.prev().removeClass('small-black-arrow-down');
            insidedrop.prev().addClass('small-black-arrow-left');
        } else {
            insidedrop.show();
            insidedrop.prev().removeClass('small-black-arrow-left');
            insidedrop.prev().addClass('small-black-arrow-down');
        }
    });

    $(".date-range-submit").on("click", function() {
        var months = ["None", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        month_start = $('[name="date-start-chooser_0"]').val();
        day_start = $('[name="date-start-chooser_1"]').val();
        year_start = $('[name="date-start-chooser_2"]').val();
        new_date_start =  months.indexOf(month_start) + "/" + day_start + "/" + year_start;

        month_end = $('[name="date-end-chooser_0"]').val();
        day_end = $('[name="date-end-chooser_1"]').val();
        year_end = $('[name="date-end-chooser_2"]').val();
        new_date_end = months.indexOf(month_end) + "/" + day_end + "/" + year_end;

        params = update_query('date', '', window.location.search);
        params = update_query('date_end', new_date_end, params);
        window.location = window.location.pathname + update_query('date_start', new_date_start, params);
    });
});

function getQueryVariable(variable) {
    var query = window.location.search.substring(1),
        vars = query.split("&");

    for (var i=0; i< vars.length; i++) {
        var pair = vars[i].split("=");
        if (pair[0] == variable) {
            return pair[1];
        }
    }

    return "";
}


function draw_donut(size) {
    // Add GET from page.load to url if any.
    var get_data = window.location.search;
    if (get_data.length)
        get_data = get_data.substr(1);
    $.ajax({
        type: "GET",
        data: get_data,
        global:false,
        url: "/prm/view/records/retrieve_records",
        success: function(dump) {
            /* Variables */
            var info = jQuery.parseJSON(dump),
                data,
                options,
                slice_options,
                show_tooltips = true;

            /* Chart Data */
            if(info.email.count > 0 || info.phone.count > 0 || info.meetingorevent.count >0) {
                data = google.visualization.arrayToDataTable([
                    ['Records',             'All Records'],
                    [info.email.name,       info.email.count],
                    [info.phone.name,       info.phone.count],
                    [info.meetingorevent.name,  info.meetingorevent.count]
                ]);
                slice_options = {0: {color: '#5eb95e'}, 1: {color: '#4bb1cf'}, 2: {color: '#faa732'}};
            } else {
                data = google.visualization.arrayToDataTable([
                    ['Records', 'All Records'],
                    ['No Records', 1]
                ]);
                slice_options = {0: {color: '#e6e6e6'}};
                show_tooltips = false;
            }

            /* Chart Options */
            if($(window).width() < 500){
                options = donut_options(250, 250, 12, 12, 225, 225, 0.6, slice_options, show_tooltips);
                $('#ajax-loading-donut').hide();
            } else {
                if(size === 'small') {
                    options = donut_options(200, 200, 12, 12, 175, 175, 0.6, slice_options, show_tooltips);
                    $('#donut-box').hide();
                } else if(size === 'big') {
                    options = donut_options(330, 350, 12, 12, 300, 330, 0.6, slice_options, show_tooltips);
                    $('#ajax-loading-donut').hide();
                }
            }

            /* Render Chart */
            var chart = new google.visualization.PieChart(document.getElementById('donutchart'));
            chart.draw(data, options);
            fill_piehole(total_records, size);
            var donut = $('#donutchart');
            visual_boxes(donut, info, size);
            add_links(donut, info, size);
            donut.fadeIn("slow");
            donut.next().fadeIn("slow");
        }
    });
}


function draw_chart() {
    // Add GET from page.load to url if any.
    var get_data = window.location.search;
    if (get_data.length) {
        get_data = get_data.substr(1);
    }
    $.ajax({
        type: "GET",
        data: get_data,
        global:false,
        url: "/prm/view/records/retrieve_referrals",
        success: function(dump){
            var info = jQuery.parseJSON(dump);
            var data = google.visualization.arrayToDataTable([
                ['Activity',      'Amount',                  { role: 'style' }],
                ['Applications',  info.applications.count,   'color: #5eb95e'],
                ['Interviews',    info.interviews.count,     'color:#4bb1cf'],
                ['Hires',         info.hires.count,          'color: #faa732'],
                ['Records',       total_ref,                 'color: #5f6c82']
            ]);
            if($(window).width() < 500){
                var options = {width: 250,
                               height: 250,
                               legend: { position: "none"},
                               chartArea: {top: 15, left: 30, height: 200, width: 210}};
            } else {
                var options = {title: 'Referral Records',
                               width: 356,
                               height: 360,
                               legend: { position: "none" },
                               chartArea: {top: 22, left: 37, height: 270, width: 290}};
            }


            var chart = new google.visualization.ColumnChart(document.getElementById('barchart'));
            chart.draw(data, options);
            var bar = $('#barchart');
            visual_boxes(bar, info, 'big');
            $('#ajax-loading-bar').hide();

            bar.fadeIn("slow");
            bar.next().fadeIn("slow");
        }
    });
}

/*
format a Date object to %m/%d/%Y
*/
function format_date(date) {
    // months are indexed at 0, while date and year are not
    return (date.getMonth() + 1) + "/" + date.getDate() + "/"
                                 + date.getFullYear();
}


function submit_date_range_from_li (e) {
    var date_start = new Date(),
        date_end = new Date(),
        days = e.currentTarget.id;
    
    if(days == 'today')
        date_start.setDate(date_start.getDate() - 1);
    else if(days == 'thirty-days')
        date_start.setDate(date_start.getDate() - 30);
    else if(days == 'ninety-days')
        date_start.setDate(date_start.getDate() - 90);
    else if(days == 'all-days')
        date_start = null

    if(date_start) {
        params = update_query('date_start', format_date(date_start),
                              window.location.search);
        params = update_query('date_end', format_date(date_end), params);
    } else {
        params = update_query('date_start', '', window.location.search);
        params = update_query('date_end', '', params);
    }

    window.location = location.pathname + params
}


function dropdown(e) {
    $('[class*=header-menu]').each(function() {
        if($(this).attr('id') != $(e.currentTarget).attr('id')){
            if($(this).hasClass('show-drop')){
                $(this).removeClass('show-drop');
            }
        }
    });
    if(!$(e.currentTarget).hasClass('show-drop')){
        $(e.currentTarget).addClass('show-drop');
        if($(window).width() < 500){
            $('.black-mask').show();
            disable_scroll('true');
        }
    } else {
        $(e.currentTarget).removeClass('show-drop');
        if($(window).width() < 500){
            $('.black-mask').hide();
        }
    }
}


function go_to_records(e) {
    url = "/prm/view/records?partner="+String(partner_id)+"&contact_type="+ e.currentTarget.id;
    if(admin_id != 'None') {
        url += '&admin=' + admin_id;
    }
    url += '&date_start=' + String(date_start) + '&date_end=' + String(date_end);
    window.location.href = url;
}


function disable_scroll(bool) {
    if($(window).width() < 500){
        if(bool == 'true'){
            $('html, body').css({'overflow': 'hidden', 'height': '100%'});
        } else if(bool == 'false') {
            $('html, body').css({'overflow': 'auto', 'height': 'auto'});
        }
    }
}


function donut_options(height, width, chartArea_top, chartArea_left, chartArea_height, chartArea_width, piehole_radius, slice_colors, show_tooltips){
    var options = {
                    legend: 'none',
                    pieHole: piehole_radius,
                    pieSliceText: 'none',
                    height: height,
                    width: width,
                    chartArea: {top:chartArea_top, left:chartArea_left, height: chartArea_height, width: chartArea_width},
                    slices: slice_colors
                  };
    if(!show_tooltips)
        options['tooltip'] = { trigger: 'none' };
    return options
}


function fill_piehole(totalrecs, size){
    var doughnut = $("#donutchart"),
        piediv = isIE8() ? doughnut.children(":first") : doughnut.find('div[dir="ltr"]');

    if(size === 'big'){
        piediv.prepend('<div class="piehole"><div class="piehole-big">'+String(totalrecs)+'</div><div class="piehole-topic">Contact Records</div><div class="piehole-filter"><a class="btn primary" id="reports-view-all">View All</a></div></div>');
    } else {
        piediv.prepend('<div class="piehole"><div class="piehole-big">'+String(totalrecs)+'</div><div class="piehole-topic">Contact Records</div><div class="piehole-filter">30 Days</div></div>');
    }
}


function visual_boxes(chart_location,json, size){
    var location = $(chart_location).next();
    if(size != 'small'){
        for(var i in json){
            location.append('<div class="chart-box" id="'+json[i].typename+'"><div class="big-num">'+String(json[i].count)+'</div><div class="reports-record-type">'+json[i].name+'</div></div>');
        }
    } else {
        for(var j in json){
            location.append('<div class="chart-box small"><div class="big-num">'+String(json[j].count)+'</div><div class="reports-record-type">'+json[j].name+'</div></div>');
        }
    }
}


function add_links(chart, json, size){
    if(size === 'big'){
        var button = $('#reports-view-all'),
            date_start = getQueryVariable("date_start"),
            date_end = getQueryVariable("date_end");

        button.attr('href', '/prm/view/records?company='
            + String(company_id)
            + '&partner=' + String(partner_id) 
            + '&date_start=' + String(date_start) 
            + '&date_end=' + String(date_end)) 
    }
}


// Shamelessly stolen from http://stackoverflow.com/a/11654596 because
// I was failing at writing my own.
function update_query(key, value, url) {
    if (!url) url = window.location.href;
    var re = new RegExp("([?&])" + key + "=.*?(&|#|$)(.*)", "gi");

    if (re.test(url)) {
        if (typeof value !== 'undefined' && value !== null)
            return url.replace(re, '$1' + key + "=" + value + '$2$3');
        else {
            var hash = url.split('#');
            url = hash[0].replace(re, '$1$3').replace(/(&|\?)$/, '');
            if (typeof hash[1] !== 'undefined' && hash[1] !== null)
                url += '#' + hash[1];
            return url;
        }
    }
    else {
        if (typeof value !== 'undefined' && value !== null) {
            var separator = url.indexOf('?') !== -1 ? '&' : '?',
                hash = url.split('#');
            url = hash[0] + separator + key + '=' + value;
            if (typeof hash[1] !== 'undefined' && hash[1] !== null)
                url += '#' + hash[1];
            return url;
        }
        else
            return url;
    }
}

// Checks to see if browser is IE8.
function isIE8() {
    var myNav = navigator.userAgent.toLowerCase();
    if (myNav.indexOf('msie') !== -1) {
        if (parseInt(myNav.split('msie')[1]) === 8) {
            return true;
        }
    }
    return false;
}
