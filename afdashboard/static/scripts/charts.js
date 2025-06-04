var options = {
    series: [
    // financial1
    {
      name: 'financial1',
      data: [
        {
          x: 'XGBOOST',
          y: [
            new Date(2022, 3, 30).getTime(),
            new Date(2024, 2, 4).getTime()
          ]
        },
      ]
    },
    // financial2
    {
      name: 'financial2',
      data: [
        {
          x: 'XGBOOST',
          y: [
            new Date(2022, 2, 4).getTime(),
            new Date(2023, 2, 4).getTime()
          ]
        },
        {
          x: 'Cointegration',
          y: [
            new Date(2022, 3, 21).getTime(),
            new Date(2023, 2, 4).getTime()
          ]
        }
      ]
    },
    // financial5
    {
      name: 'financial5',
      data: [
        {
          x: 'XGBOOST',
          y: [
            new Date(2023, 2, 4).getTime(),
            new Date(2023, 2, 4).getTime()
          ]
        },
        {
          x: 'Cointegration',
          y: [
            new Date(2022, 2, 4).getTime(),
            new Date(2023, 2, 4).getTime()
          ]
        },
        {
          x: 'Dart',
          y: [
            new Date(2022, 2, 22).getTime(),
            new Date(2022, 11, 31).getTime()
          ]
        }
      ]
    },
    // your_account
    {
      name: 'mirrorx1',
      data: [
        {
          x: 'Cointegration',
          y: [
            new Date(2022, 2, 4).getTime(),
            new Date(2024, 2, 4).getTime()
          ]
        }
      ]
    },
    // your_account
    {
      name: 'mirrorx2',
      data: [
        {
          x: 'Cointegration',
          y: [
            new Date(2023, 2, 4).getTime(),
            new Date(2024, 3, 20).getTime()
          ]
        }
      ]
    },
    // your_account
    {
      name: 'mirrorx3',
      data: [
        {
          x: 'Dart',
          y: [
            new Date(2022, 8, 25).getTime(),
            new Date(2023, 2, 22).getTime()
          ]
        }
      ]
    },
    // your_account
    {
      name: 'mirrorx4',
      data: [
        {
          x: 'Dart',
          y: [
            new Date(2022, 0, 2).getTime(),
            new Date(2022, 7, 20).getTime()
          ]
        }
      ]
    },
    // your_account
    {
      name: 'mirrorx5',
      data: [
        {
          x: 'Dart',
          y: [
            new Date(2022, 7, 20).getTime(),
            new Date(2024, 4, 12).getTime()
          ]
        }
      ]
    },
    // your_account
    {
      name: 'mirrorxfund',
      data: [
        {
          x: 'Dart',
          y: [
            new Date(2023, 4, 13).getTime(),
            new Date(2023, 5, 5).getTime()
          ]
        }
      ]
    },
    // your_account
    {
      name: 'team',
      data: [
        {
          x: 'Dart',
          y: [
            new Date(2023, 5, 13).getTime(),
            new Date(2024, 2, 4).getTime()
          ]
        }
      ]
    },
    // financial3
    {
      name: 'financial3',
      data: [
        {
          x: 'Dart',
          y: [
            new Date(2023, 2, 5).getTime(),
            new Date(2023, 4, 1).getTime()
          ]
        }
      ]
    },
    // financial4
    {
      name: 'financial4',
      data: [
        {
          x: 'Dart',
          y: [
            new Date(2023, 4, 2).getTime(),
            new Date(2023, 2, 3).getTime()
          ]
        }
      ]
    },
  ],
    chart: {
    height: 350,
    type: 'rangeBar'
  },
  plotOptions: {
    bar: {
      horizontal: true,
      barHeight: '50%',
      rangeBarGroupRows: true
    }
  },
  colors: [
    "#008FFB", "#00E396", "#FEB019", "#FF4560", "#775DD0",
    "#3F51B5", "#546E7A", "#D4526E", "#8D5B4C", "#F86624",
    "#D7263D", "#1B998B", "#2E294E", "#F46036", "#E2C044"
  ],
  fill: {
    type: 'solid'
  },
  xaxis: {
    type: 'datetime'
  },
  legend: {
    position: 'right'
  },
  tooltip: {
    custom: function(opts) {
      const fromYear = new Date(opts.y1).getFullYear()
      const toYear = new Date(opts.y2).getFullYear()
      const values = opts.ctx.rangeBar.getTooltipValues(opts)
  
      return (
        '<div class="apexcharts-tooltip-rangebar">' +
        '<div> <span class="series-name" style="color: ' +
        values.color +
        '">' +
        (values.seriesName ? values.seriesName : '') +
        '</span></div>' +
        '<div> <span class="category">' +
        values.ylabel +
        ' </span> <span class="value start-value">' +
        fromYear +
        '</span> <span class="separator">-</span> <span class="value end-value">' +
        toYear +
        '</span></div>' +
        '</div>'
      )
    }
  }
  };

  var chart = new ApexCharts(document.querySelector("#timeline"), options);
  chart.render();

  var options = {
    series: [{
    name: 'Series 1',
    data: [80, 50, 30, 40, 100, 20],
  }],
    chart: {
    height: 350,
    type: 'radar',
  },
  title: {
    text: 'financial Winrate Per Month'
  },
  xaxis: {
    categories: ['January', 'February', 'March', 'April', 'May', 'June']
  }
  };

  var chart = new ApexCharts(document.querySelector("#radar"), options);
  chart.render();

  var options = {
    series: [{
    name: "BTCUSDT",
    data: [
    [16.4, 5.4], [21.7, 2], [25.4, 3], [19, 2], [10.9, 1], [13.6, 3.2], [10.9, 7.4], [10.9, 0], [10.9, 8.2], [16.4, 0], [16.4, 1.8], [13.6, 0.3], [13.6, 0], [29.9, 0], [27.1, 2.3], [16.4, 0], [13.6, 3.7], [10.9, 5.2], [16.4, 6.5], [10.9, 0], [24.5, 7.1], [10.9, 0], [8.1, 4.7], [19, 0], [21.7, 1.8], [27.1, 0], [24.5, 0], [27.1, 0], [29.9, 1.5], [27.1, 0.8], [22.1, 2]]
  },{
    name: "BNBUSDT",
    data: [
    [36.4, 13.4], [1.7, 11], [5.4, 8], [9, 17], [1.9, 4], [3.6, 12.2], [1.9, 14.4], [1.9, 9], [1.9, 13.2], [1.4, 7], [6.4, 8.8], [3.6, 4.3], [1.6, 10], [9.9, 2], [7.1, 15], [1.4, 0], [3.6, 13.7], [1.9, 15.2], [6.4, 16.5], [0.9, 10], [4.5, 17.1], [10.9, 10], [0.1, 14.7], [9, 10], [12.7, 11.8], [2.1, 10], [2.5, 10], [27.1, 10], [2.9, 11.5], [7.1, 10.8], [2.1, 12]]
  },{
    name: "ETHUSDT",
    data: [
    [21.7, 3], [23.6, 3.5], [24.6, 3], [29.9, 3], [21.7, 20], [23, 2], [10.9, 3], [28, 4], [27.1, 0.3], [16.4, 4], [13.6, 0], [19, 5], [22.4, 3], [24.5, 3], [32.6, 3], [27.1, 4], [29.6, 6], [31.6, 8], [21.6, 5], [20.9, 4], [22.4, 0], [32.6, 10.3], [29.7, 20.8], [24.5, 0.8], [21.4, 0], [21.7, 6.9], [28.6, 7.7], [15.4, 0], [18.1, 0], [33.4, 0], [16.4, 0]]
  }],
    chart: {
    height: 350,
    type: 'scatter',
    zoom: {
      enabled: true,
      type: 'xy'
    }
  },
  xaxis: {
    tickAmount: 10,
    labels: {
      formatter: function(val) {
        return parseFloat(val).toFixed(1)
      }
    }
  },
  yaxis: {
    tickAmount: 7
  }
  };

  var chart = new ApexCharts(document.querySelector("#scatter"), options);
  chart.render();

  var options = {
    series: [
    {
      type: 'boxPlot',
      data: [
        {
          x: 'Jan 2022',
          y: [54, 66, 69, 75, 88]
        },
        {
          x: 'Jan 2022',
          y: [43, 65, 69, 76, 81]
        },
        {
          x: 'Jan 2023',
          y: [31, 39, 45, 51, 59]
        },
        {
          x: 'Jan 2023',
          y: [39, 46, 55, 65, 71]
        },
        {
          x: 'Jan 2023',
          y: [29, 31, 35, 39, 44]
        },
        {
          x: 'Jan 2024',
          y: [41, 49, 58, 61, 67]
        },
        {
          x: 'Jan 2024',
          y: [54, 59, 66, 71, 88]
        }
      ]
    }
  ],
    chart: {
    type: 'boxPlot',
    height: 350
  },
  title: {
    text: 'Pairs Trading Profit',
    align: 'left'
  },
  plotOptions: {
    boxPlot: {
      colors: {
        upper: '#5C4742',
        lower: '#A5978B'
      }
    }
  }
  };

  var chart = new ApexCharts(document.querySelector("#boxplot"), options);
  chart.render();