

function create_piehole(){
    var data = google.visualization.arrayToDataTable([
    ['Records', 'All Records'],
    ['Email',     5],
    ['Phone Calls',      2],
    ['Face to Face',  2]
    ]);

    var options = {
        legend: 'none',
        pieHole: 0.6,
        pieSliceText: 'none',
        height: 180,
        width: 180,
        chartArea: {top:10, left:10, width: 155, height: 155},
        slices: {0: {color: '#48DD00'}, 1: {color: '#FF5C00'}, 2: {color: '#B90091'}}
    };

    var chart = new google.visualization.PieChart(document.getElementById('donutchart'));
    chart.draw(data, options);
}