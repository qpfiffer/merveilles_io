function build_charts() {
    $('#last_10_days').highcharts({
        chart: {
            type: 'spline',
            backgroundColor: '#DDD'
        },
        title: {
            text: 'Posts in the last 10 days',
            style: {
                color: '#111'
            }
        },
        plotOptions: {
            spline: {
                pointInterval: 86400000, // one day
                pointStart: start_date
            }
        },
        tooltip: {
            formatter: function() {
                    return '<b>'+ this.series.name +'</b><br/>'+
                    Highcharts.dateFormat('%e. %b', this.x) +': '+ this.y +' links';
            }
        },
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: { // don't display the dummy year
                month: '%e. %b',
                year: '%b'
            }
        },
        yAxis: {
            min: 0,
        },
        series: stats_ten
    });
    $('#activity_by_hour').highcharts({
        chart: {
            type: 'column',
            backgroundColor: '#DDD'
        },
        title: {
            text: false,
            style: {
                color: '#111'
            }
        },
        tooltip: {
            formatter: function() {
                    return '<b>'+ this.series.name +'</b><br/>'+
                    + this.y +' total links';
            }
        },
        yAxis: {
            min: 0,
        },
        series: hourly_activity
    });
    $('#last_day').highcharts({
        chart: {
            type: 'spline',
            backgroundColor: '#DDD'
        },
        title: {
            text: false,
            style: {
                color: '#111'
            }
        },
        tooltip: {
            formatter: function() {
                    return '<b>'+ this.series.name +'</b><br/>'+
                    Highcharts.dateFormat('%e. %b', this.x) +': '+ this.y +' links';
            }
        },
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: { // don't display the dummy year
                month: '%e. %b',
                year: '%b'
            }
        },
        yAxis: {
            min: 0,
        },
        series: stats
    });
}
