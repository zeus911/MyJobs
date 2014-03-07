$(function() {
    var AppView = Backbone.View.extend({
        el: $("body"),

        events: {
            "click #email": "go_to_records",
            "click #phone": "go_to_records",
            "click #facetoface": "go_to_records"
        },

        go_to_records: function(e) {
            window.location.href = "/prm/view/reports/details/records/?company="+String(company_id)+"&partner="+String(partner_id)+"&record_type="+ e.currentTarget.id;
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
        },

        draw_donut: function(size) {
            $.ajax({
                type: "GET",
                data: {company: company_id,
                       partner: partner_id},
                global:false,
                url: "/prm/view/records/retrieve_records",
                success: function(dump){
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
                        $('#donut-box').hide();
                    } else if(size === 'big'){
                        options = donut_options(330, 360, 12, 12, 300, 330, 0.6);
                        $('#ajax-loading-donut').hide();
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

                    var options = {title: 'Referral Records',
                                   width: 356,
                                   height: 360,
                                   legend: { position: "none" },
                                   chartArea: {top: 22, left: 37, height: 270, width: 290}};


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

    });
    var App = new AppView;
});

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
