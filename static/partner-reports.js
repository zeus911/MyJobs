$(function() {
    var AppView = Backbone.View.extend({
        el: $("body"),

        initialize: function() {
            _.bindAll(this, 'render');
            this.page = $('.prm-header').children(':first').html();
            this.render();
        },

        render: function() {
            if(this.page === 'Overview'){
                draw_donut('small', 'sample');
            }
            if(this.page === 'Reports'){
                draw_donut('big', 'sample');
                draw_chart();
            }
        }

    });
    var App = new AppView;
});

function draw_donut(size) {
    var company_id = $('#company').val();
    var partner_id = $('#partner').val();
    $.ajax({
        type: "GET",
        data: {company: company_id,
               partner: partner_id},
        global:false,
        url: "/prm/view/records/retrieve_records",
        success: function(dump){
            console.log(dump);
            var info = jQuery.parseJSON(dump);
            var data = google.visualization.arrayToDataTable([
                            ['Records',             'All Records'],
                            [info.email.name,       info.email.count],
                            [info.phone.name,       info.phone.count],
                            [info.facetoface.name,  info.facetoface.count]
                        ]);

            var options;
            if(size === 'small'){
                options = donut_options(200, 200, 12, 12, 175, 175, 0.6);
                $('#donut-box').children(":first").hide();
            } else if(size === 'big'){
                options = donut_options(330, 360, 12, 12, 300, 330, 0.6);
                $('#ajax-loading-donut').hide();
            }
            var chart = new google.visualization.PieChart(document.getElementById('donutchart'));
            chart.draw(data, options);
            fill_piehole($('#cr-count').val());

            var donut = $('#donutchart');
            visual_boxes(donut, info, size);
            donut.fadeIn("slow");
            donut.next().fadeIn("slow");
        }
    });
}

function draw_chart() {
    var company_id = $('#company').val();
    var partner_id = $('#partner').val();
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
                            ['Records',       $('#ref-count').val(),     'color: #5f6c82']
                        ]);

            var options = {title: 'Referral Records',
                           width: 356,
                           height: 360,
                           legend: { position: "none" },
                           chartArea: {top: 22, left: 37, height: 270, width: 290}};


            var chart = new google.visualization.ColumnChart(document.getElementById('barchart'));
            chart.draw(data, options);
            fill_piehole(info.totalrecs);
            var bar = $('#barchart');
            visual_boxes(bar, info, 'big');
            $('#ajax-loading-bar').hide();

            bar.fadeIn("slow");
            bar.next().fadeIn("slow");
        }
    });
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

function fill_piehole(totalrecs){
    var doughnut = $("#donutchart");
    var piediv = doughnut.children(":first-child").children(":first-child");
    piediv.prepend('<div class="piehole"><div class="piehole-big">'+String(totalrecs)+'</div><div class="piehole-topic">Contact Records</div><div class="piehole-filter">30 Days</div></div>');
}

function visual_boxes(chart_location,json, size){
    var location = $(chart_location).next();
    if(size != 'small'){
        for(var i in json){
            location.append('<div class="chart-box"><div class="big-num">'+String(json[i].count)+'</div><div class="reports-record-type">'+json[i].name+'</div></div>');
        }
    } else {

    }
}
