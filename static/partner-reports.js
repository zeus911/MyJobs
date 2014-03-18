$(function() {
    var AppView = Backbone.View.extend({
        el: $("body"),

        events: {
            "click #email": "go_to_records",
            "click #phone": "go_to_records",
            "click #facetoface": "go_to_records",
            "click #job": "go_to_records",
            "click .header-menu": "dropdown",
            "click #date-drop": "date_drop",
            "click #custom-date-dropdown": "prevent_close",
            "click .black-mask": "close_drop_and_restore_scroll",
            "click #today": "submit_date_range_from_li",
            "click #thirty-days": "submit_date_range_from_li",
            "click #ninety-days": "submit_date_range_from_li",
            "click .date-range-submit": "submit_date_range"
        },

        submit_date_range: function(e) {
            var months = ["None", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
            month_start = $('[name="date-start-chooser_0"]').val();
            day_start = $('[name="date-start-chooser_1"]').val();
            year_start = $('[name="date-start-chooser_2"]').val();
            new_date_start =  months.indexOf(month_start) + "/" + day_start + "/" + year_start;

            month_end = $('[name="date-end-chooser_0"]').val();
            day_end = $('[name="date-end-chooser_1"]').val();
            year_end = $('[name="date-end-chooser_2"]').val();
            new_date_end = months.indexOf(month_end) + "/" + day_end + "/" + year_end;

            params = update_query('date_start', new_date_start, window.location.search)
            window.location = '/prm/view/reports/details' + update_query('date_start', new_date_start, params)
        },

        submit_date_range_from_li: function(e) {
            days = e.currentTarget.id;
            if(days == 'today') {
                range = 1;
            }
            else if(days == 'thirty-days') {
                range = 30;
            }
            else if(days == 'ninety-days') {
                range = 90;
            }
            window.location = '/prm/view/reports/details' + update_query('date', range, window.location.search)
        },


        go_to_records: function(e) {
            url = "/prm/view/reports/details/records/?company="+String(company_id)+"&partner="+String(partner_id)+"&record_type="+ e.currentTarget.id;
            if(admin_id != 'None') {
                url += '&admin=' + admin_id;
            }
            url += '&date_start=' + String(date_start) + '&date_end=' + String(date_end);
            window.location.href = url;
        },

        initialize: function() {
            _.bindAll(this, 'render');
            this.page = $('.prm-header').children(':first').html();
            $( ".datepicker" ).datepicker();
            this.render();
        },

        render: function() {
            if(this.page === 'Overview'){
                this.draw_donut('small');
            }
            if(this.page === 'Reports'){
                this.draw_donut('big');
                this.draw_chart();
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
        },

        draw_donut: function(size) {
            $.ajax({
                type: "GET",
                data: {company: company_id,
                       partner: partner_id},
                global:false,
                url: "/prm/view/records/retrieve_records",
                success: function(dump) {
                    var info = jQuery.parseJSON(dump);
                    var data = google.visualization.arrayToDataTable([
                                    ['Records',             'All Records'],
                                    [info.email.name,       info.email.count],
                                    [info.phone.name,       info.phone.count],
                                    [info.facetoface.name,  info.facetoface.count]
                                ]);

                    var options;
                    if($(window).width() < 500){
                        options = donut_options(250, 250, 12, 12, 225, 225, 0.6);
                        $('#ajax-loading-donut').hide();
                    } else {
                        if(size === 'small') {
                            options = donut_options(200, 200, 12, 12, 175, 175, 0.6);
                            $('#donut-box').hide();
                        } else if(size === 'big') {
                            options = donut_options(330, 350, 12, 12, 300, 330, 0.6);
                            $('#ajax-loading-donut').hide();
                        }
                    }
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
        },

        draw_chart: function() {
            $.ajax({
                type: "GET",
                data: {company: company_id,
                       partner: partner_id},
                global:false,
                url: "/prm/view/records/retrieve_referrals",
                success: function(dump){
                    var info = jQuery.parseJSON(dump);
                    var data = google.visualization.arrayToDataTable([
                                    ['Activity',      'Amount',                  { role: 'style' }],
                                    ['Applications',  info.applications.count,   'color: #5eb95e'],
                                    ['Interviews',    info.interviews.count,     'color:#4bb1cf'],
                                    ['Hires',         info.hires.count,          'color: #faa732'],
                                    ['Records',       total_ref,     'color: #5f6c82']
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
        },

        dropdown: function(e) {
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
        },

        date_drop: function(e){
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
        },

        close_drop_and_restore_scroll: function(e){
            if($(window).width() < 500){
                $('.black-mask').hide();
                disable_scroll('false');
                $('[class*=header-menu]').removeClass('show-drop');
            }
        },

        prevent_close: function(e){
            e.stopPropagation();
        }

    });
    var App = new AppView;
});

function disable_scroll(bool) {
    if($(window).width() < 500){
        if(bool == 'true'){
            $('html, body').css({'overflow': 'hidden', 'height': '100%'});
        } else if(bool == 'false') {
            $('html, body').css({'overflow': 'auto', 'height': 'auto'});
        }
    }
}

function donut_options(height, width, chartArea_top, chartArea_left, chartArea_height, chartArea_width, piehole_radius){
    var options = {
                    legend: 'none',
                    pieHole: piehole_radius,
                    pieSliceText: 'none',
                    height: height,
                    width: width,
                    chartArea: {top:chartArea_top, left:chartArea_left, height: chartArea_height, width: chartArea_width},
                    slices: {0: {color: '#5eb95e'}, 1: {color: '#4bb1cf'}, 2: {color: '#faa732'}}
                  };
    return options
}

function fill_piehole(totalrecs, size){
    var doughnut = $("#donutchart");
    var piediv = doughnut.children(":first-child").children(":first-child");
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
        var button = $('#reports-view-all');
        button.attr('href', '/prm/view/reports/details/records/?company='+String(company_id)+'&partner='+String(partner_id));
    }
}

function update_query(param, val, search) {
    var re = new RegExp("([?;&])" + param + "[^&;]*[;&]?")
    var query_string = search.replace(re, "$1").replace(/&$/, '');
    return (query_string.length > 2 ? query_string + "&" : "?") + param + "=" + val;
 }