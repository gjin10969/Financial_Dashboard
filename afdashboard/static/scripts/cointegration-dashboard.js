import { updateNavigationData1, updateNavigationData2 } from './cointegration-navigation.js';
import { fetch_data, get_coint_data } from './api.js';

let chart1, ctx1; // Global variable to store the chart instance

window

async function updateCharts(data) {
    createCumulativeLineChart(data, ctx1);
    calculateNegativePnl(data);
    calculateProfitLossMetrics(data);
}

export async function coint_livedata_metrics() {
    try {
        // const response = await fetchJsonFromSupabase();
        const navigationData = await get_coint_data();
        
        await updateNavigationData1(navigationData);
        await updateNavigationData2(navigationData);
        console.log(navigationData);
    } catch (error) {
        console.error('Error:', error);
    }
}


// async function refreshDashboard() {
//   try {
//       const response = await fetch_data(); // Fetch data using abort signal

//       const dataToFilter = response.filtered_data || [];
//       console.log(dataToFilter);

//       const your_accountData = dataToFilter.filter(item => 
//         item.mirrorx_account === 'your_account'
//       );
//       const your_accountData = dataToFilter.filter(item => 
//         item.mirrorx_account === 'your_account'
//       );
//       console.log(your_accountData);
//       console.log(your_accountData);

//       // Now use the filtered data for mirrorx_account
//       await updateCharts(your_accountData); // Update chart with filtered data

//   } catch (error) {
//       console.error('Error:', error);
//   }
// }

// Trigger the chart creation on page load or when new data is available
$(document).ready(function () {
    ctx1 = document.getElementById('pnl-chart');

    if (!window.filtered_activated){
        coint_livedata_metrics();
    } else {

    }
});

async function dashboard_data(response) {

  try {

      let accountsData = response.overall;
      console.log(accountsData);

      let responseData = response.response_data;
      console.log(responseData);

      // Winning Rate
      $('#win_rate').text(response.winning_rate_acc.your_account);

  } catch (error) {
      console.error("Error in dashboard_data function:", error);
      // Handle the error, you can show a message to the user or retry the request
      // Example: alert("An error occurred while fetching data.");
  }
}

function calculateNegativePnl(data) {
    let negativePnlPerTimestamp = {};
    let losingDaysCount = 0;
    let totalLoss = 0;

    data.forEach(item => {
        let timestamp = item.date; // Use full timestamp

        // Rename "mirrorxtotal" to "ALL ACCOUNTS"
        let account = item.mirrorx_account === "mirrorxtotal" ? "ALL ACCOUNTS" : item.mirrorx_account;

        // Check if the realizedPnl is negative
        if (item.realizedPnl < 0) {
            if (!negativePnlPerTimestamp[account]) {
                negativePnlPerTimestamp[account] = {};
            }
            if (!negativePnlPerTimestamp[account][timestamp]) {
                negativePnlPerTimestamp[account][timestamp] = { value: 0, symbol: item.symbol };
            }

            negativePnlPerTimestamp[account][timestamp].value += item.realizedPnl;
            totalLoss += item.realizedPnl;
            losingDaysCount++;
        }
    });

    // Calculate the average loss
    let averageLoss = losingDaysCount > 0 ? totalLoss / losingDaysCount : 0;

    console.log("Negative PNL Data:", negativePnlPerTimestamp); // Debug statement
    console.log("Losing Days Count:", losingDaysCount);
    console.log("Average Loss:", averageLoss);

    // Losing Days
    $('#total_losing_days').text(losingDaysCount);

    // Average Loss
    $('#average_loss').text(averageLoss.toFixed(2));

    return {
        negativePnlPerTimestamp,
        losingDaysCount,
        averageLoss
    };
}

function calculateProfitLossMetrics(data) {
    let totalProfit = 0;
    let totalLoss = 0;
    let profitDaysCount = 0;
    let lossDaysCount = 0;
    let totalProfitDays = 0; // To calculate average profit
    let totalLossDays = 0; // To calculate average loss

    // Create a map to hold cumulative PNL per date per account
    let cumulativePnlMap = {};

    data.forEach(item => {
        let timestamp = item.date; // Use full timestamp

        // Rename "mirrorxtotal" to "ALL ACCOUNTS"
        let account = item.mirrorx_account === "mirrorxtotal" ? "ALL ACCOUNTS" : item.mirrorx_account;

        // Initialize the account and timestamp in the cumulativePnlMap if not present
        if (!cumulativePnlMap[account]) {
            cumulativePnlMap[account] = {};
        }
        if (!cumulativePnlMap[account][timestamp]) {
            cumulativePnlMap[account][timestamp] = 0;
        }

        // Accumulate realizedPnl per timestamp
        cumulativePnlMap[account][timestamp] += item.realizedPnl;
    });

    // Iterate through the cumulative PNL map to calculate total profit, total loss
    for (let account in cumulativePnlMap) {
        for (let timestamp in cumulativePnlMap[account]) {
            let pnl = cumulativePnlMap[account][timestamp];
            if (pnl > 0) {
                totalProfit += pnl;
                profitDaysCount++;
                totalProfitDays += pnl; // For average profit calculation
            } else if (pnl < 0) {
                totalLoss += pnl;
                lossDaysCount++;
                totalLossDays += pnl; // For average loss calculation
            }
        }
    }

    // Calculate profit/loss ratio
    let profitLossRatio = totalLoss !== 0 ? (totalProfit / Math.abs(totalLoss)) : Infinity;

    // Calculate average profit and loss
    let averageProfit = profitDaysCount > 0 ? totalProfitDays / profitDaysCount : 0;
    let averageLoss = lossDaysCount > 0 ? totalLossDays / lossDaysCount : 0;

    // Calculate net profit/loss
    let netProfitLoss = totalProfit + totalLoss;

    console.log("Total Profit:", totalProfit);
    console.log("Total Loss:", totalLoss);
    console.log("Net Profit/Loss:", netProfitLoss);
    console.log("Profit/Loss Ratio:", profitLossRatio);
    console.log("Average Profit:", averageProfit);
    console.log("Average Loss:", averageLoss);

    // Total Profit
    $('#total_profit').text(totalProfit.toFixed(2));

    // Total Loss
    $('#total_loss').text(totalLoss.toFixed(2));

    // Profit/Loss Ratio
    $('#profit_loss_ratio').text(profitLossRatio.toFixed(2));

    // Average Profit
    $('#average_profit').text(averageProfit.toFixed(2));

    // Net Profit/Loss
    $('#net_profit_loss').text(netProfitLoss.toFixed(2));

    return {
        totalProfit,
        totalLoss,
        netProfitLoss,
        profitLossRatio,
        averageProfit,
        averageLoss
    };
}

function calculateCumulativePnl(data) {
    let cumulativePnlPerTimestamp = {};

    data.forEach(item => {
        let timestamp = item.date; // Use full timestamp

        // Rename "mirrorxtotal" to "ALL ACCOUNTS"
        let account = item.mirrorx_account === "mirrorxtotal" ? "ALL ACCOUNTS" : item.mirrorx_account;

        if (!cumulativePnlPerTimestamp[account]) {
            cumulativePnlPerTimestamp[account] = {};
        }
        if (!cumulativePnlPerTimestamp[account][timestamp]) {
            cumulativePnlPerTimestamp[account][timestamp] = { value: 0, symbol: item.symbol };
        }
        cumulativePnlPerTimestamp[account][timestamp].value += item.realizedPnl;
    });

    console.log("Cumulative PNL Data:", cumulativePnlPerTimestamp); // Debug statement

    return { cumulativePnlPerTimestamp };
}

function createCumulativeLineChart(data, ctx) {
    if (chart1) {
        chart1.destroy(); // Destroy previous instance if exists
    }

    let { cumulativePnlPerTimestamp } = calculateCumulativePnl(data);

    let seriesData = [];

    Object.keys(cumulativePnlPerTimestamp).forEach(account => {
        let aggregatedData = {};
        Object.entries(cumulativePnlPerTimestamp[account]).forEach(([date, { value }]) => {
            let timestamp = new Date(date).getTime();
            let hour = new Date(date).getHours();

            // Find the closest 4-hour boundary
            let nearestBoundary = Math.floor(hour / 4) * 4;
            let aggregateTimestamp = new Date(date);
            aggregateTimestamp.setHours(nearestBoundary);
            aggregateTimestamp.setMinutes(0);
            aggregateTimestamp.setSeconds(0);
            aggregateTimestamp.setMilliseconds(0);

            let aggregatedTimestamp = aggregateTimestamp.getTime();

            if (!aggregatedData[aggregatedTimestamp]) {
                aggregatedData[aggregatedTimestamp] = { timestamp: aggregatedTimestamp, value: 0 };
            }
            aggregatedData[aggregatedTimestamp].value += value;
        });

        let cumulativeValue = 0;
        let accountSeriesData = Object.values(aggregatedData)
            .map(({ timestamp, value }) => {
                cumulativeValue += value;
                return { x: timestamp, y: cumulativeValue };
            });

        seriesData.push({
            name: `${account.toUpperCase()}`,
            data: accountSeriesData
        });
    });

    console.log("Line Chart Series Data:", seriesData); // Debug statement

    let options = {
        series: seriesData,
        chart: {
            type: 'area',
            stacked: false,
            height: 350,
            zoom: {
                type: 'x',
                enabled: true,
                autoScaleYaxis: true
            },
            toolbar: {
                autoSelected: 'zoom'
            },
            animations: {
                enabled: true
            }
        },
        grid: {
            borderColor: 'rgba(255, 255, 255, 0.1)',
            offsetY: -5
        },
        title: {
            text: 'Time Series Pnl Movement',
            align: 'center',
            style: {
                fontFamily: 'sans-serif',
                color: '#f2f2f2'
            }
        },
        yaxis: {
            labels: {
                style: {
                    colors: '#57584a',
                },
                formatter: function (value) {
                    let formattedValue = Math.abs(value).toFixed(3); // Format to 3 decimal places
                    if (value < 0) {
                        return '-$' + formattedValue; // Add dollar sign before the absolute value of negative numbers
                    } else {
                        return '$' + formattedValue; // Add dollar sign before positive numbers
                    }
                }
            },
        },
        xaxis: {
            labels: {
                style: {
                    colors: '#57584a'
                }
            },
            type: 'datetime'
        },
        fill: {
            type: 'gradient',
            gradient: {
                shadeIntensity: 1,
                inverseColors: false,
                opacityFrom: 0.7,
                opacityTo: 0,
                stops: [0, 90, 100]
            }
        },
        stroke: {
            curve: 'smooth', // Smooth curve for waveform effect
            width: 2
        },
        dataLabels: {
            enabled: false
        },
        markers: {
            size: 0,
        },
        tooltip: {
            enabled: true,
            shared: true,
            intersect: false,
            x: {
                format: 'dd MMM yyyy HH:mm'
            },
            y: {
                formatter: function (value) {
                    let formattedValue = Math.abs(value).toFixed(3);
                    let pnlLabel = value < 0 ? '-$' + formattedValue : '$' + formattedValue;
                    return pnlLabel;
                }
            }
        },
    };

    chart1 = new ApexCharts(ctx, options);
    chart1.render();
}
  

export {updateCharts, fetch_data};