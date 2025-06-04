// import ApexCharts from 'apexcharts';
import { updateFilteredData, updateAccountMetrics} from './navigation.js'
import {fetch_data, initial_load} from './api.js'
import { showSpinner, hideSpinner } from './datefilter.js';

let ctx1, ctx2, chart1, chart2;

// Refactored functions with meaningful variable names

async function updateCharts(tradeData) {
    createCumulativeLineChart(tradeData, ctx1);
    createCumulativeBarChart(tradeData, ctx2);
    console.log(tradeData);
}

async function updateGaugeCharts(winRateData) {
    createGaugeCharts(winRateData);
}

async function updatePolarAreaChart(winningRateData) {
    createPolarAreaChart(winningRateData);
}

async function updateTradeTable(tradeData) {
    createTradesTable(tradeData);
}

async function updateProfitableTable(profitData) {
    createProfitableTable(profitData);
}

async function updateUnprofitableTable(lossData) {
    createUnprofitableTable(lossData);
}

async function updateBuySellTable(buySellData) {
    createBuySellTable(buySellData);
}

// Main refresh function
async function refreshData() {
    try {
        await showSpinner(); // Show the spinner before starting data processing

        const response = await fetch_data(); // Fetch data using abort signal
        const allData = response.filtered_data.filter(item => item.mirrorx_account === "mirrorxtotal");

        if (window.filtered_activated) {
            await updateCharts(response.filtered_data);
        } else {
            await updateCharts(allData);
        }

        await updateGaugeCharts(response.symbols_winrate);
        await updatePolarAreaChart(response.winning_rate_acc);
        await updateTradeTable(response.trades_account);
        await updateProfitableTable(response.profits_by_coin);
        await updateUnprofitableTable(response.profits_by_coin); // Assuming different unprofitable data
        await updateBuySellTable(response.response_data.calculate_buy_sell);
        await updateFilteredData(response); // Additional filtered data processing

    } catch (error) {
        console.error('Error:', error);
    } finally {
        await hideSpinner(); // Hide the spinner after all updates are done
    }
}

export async function allAccountData() {
    try {
        await showSpinner(); // Show the spinner before starting data processing

        const response = await fetch_data(); // Fetch data using abort signal
        const allData = response.filtered_data.filter(item => item.mirrorx_account === "mirrorxtotal");

        await updateCharts(allData);
        await updateGaugeCharts(response.symbols_winrate);
        await updatePolarAreaChart(response.winning_rate_acc);
        await updateTradeTable(response.trades_account);
        await updateProfitableTable(response.profits_by_coin);
        await updateUnprofitableTable(response.profits_by_coin); // Assuming different unprofitable data
        await updateBuySellTable(response.response_data.calculate_buy_sell);
        await updateFilteredData(response); // Additional filtered data processing

    } catch (error) {
        console.error('Error:', error);
    } finally {
        await hideSpinner(); // Hide the spinner after all updates are done
    }
}


export async function livedata_metrics() {
    try {
        // const response = await fetchJsonFromSupabase();
        const navigationData = await initial_load();
        await updateAccountMetrics(navigationData);
        await updateFilteredData(navigationData); // Additional filtered data processing

    } catch (error) {
        console.error('Error:', error);
    }
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

function createCumulativeBarChart(data, ctx) {
    if (chart2) {
        chart2.destroy(); // Destroy previous instance if exists
    }

    let { cumulativePnlPerTimestamp } = calculateCumulativePnl(data);

    let seriesData = [];
    let categories = [];

    Object.keys(cumulativePnlPerTimestamp).forEach(account => {
        let aggregatedValues = {};
        for (let date in cumulativePnlPerTimestamp[account]) {
            let formattedDate = formatDate(new Date(date));
            if (!aggregatedValues[formattedDate]) {
                aggregatedValues[formattedDate] = 0;
            }
            aggregatedValues[formattedDate] += cumulativePnlPerTimestamp[account][date].value;
        }

        for (let date in aggregatedValues) {
            if (aggregatedValues[date] === 0) {
                delete aggregatedValues[date];
            }
        }

        categories = Object.keys(aggregatedValues);
        let values = Object.values(aggregatedValues);

        seriesData.push({
            name: `${account.toUpperCase()}`,
            data: values
        });
    });

    console.log("Bar Chart Series Data:", seriesData); // Debug statement

    let options = {
        series: seriesData,
        chart: {
            type: 'bar',
            height: 350,
            animations: {
                enabled: true
            }
        },
        grid: {
            borderColor: 'rgba(255, 255, 255, 0.1)', // Set the color of x-axis grid lines
            offsetY: -5 // Adjust the visibility by changing the offset
        },
        title: {
            text: 'Daily Pnl Movement',
            align: 'center',
            style: {
                color: '#f2f2f2',
                fontFamily: 'sans-serif'
            }
        },
        plotOptions: {
            bar: {
                columnWidth: '80%',
            }
        },
        dataLabels: {
            enabled: false,
        },
        markers: {
            size: 0
        },
        yaxis: {
            labels: {
                style: {
                    colors: '#57584a' // Set y-axis label color to the specified color
                },
                formatter: function (value) {
                    if (value < 0) {
                        return '-$' + Math.abs(Math.round(value)); // Add dollar sign before the absolute value of negative numbers
                    } else {
                        return '$' + Math.round(value); // Add dollar sign before positive numbers
                    }
                }
            }
        },
        xaxis: {
            type: 'category',
            categories: categories,
            labels: {
                style: {
                    colors: '#57584a' // Set x-axis label color to the specified color
                }
            }
        },
        tooltip: {
            x: {
                formatter: function (val) {
                    return val; // Display the full date in the tooltip
                }
            }
        }
    };

    chart2 = new ApexCharts(ctx, options);
    chart2.render();
}

// UTC TIME DON'T CHANGE

function formatDate(date) {
    const options = {
        timeZone: 'UTC',
        month: 'short',
        day: '2-digit'
    };
    return date.toLocaleDateString('en-US', options);
}

// Global variable to store previous win rates
let previousWinRatePerSymbol = {};

function createGaugeCharts(winRateData) {
    const winRatePerSymbol = winRateData; // Access the win_rate_per_symbol data

    const symbols = Object.keys(winRatePerSymbol);
    const seriesValues = Object.values(winRatePerSymbol);

    // Calculate the number of gauge charts to display
    const numGaugeCharts = symbols.length;

    // Calculate the number of empty columns for centering
    const emptyColumns = Math.max(0, 13 - numGaugeCharts);

    // Calculate the width for each gauge chart column
    const columnWidth = Math.floor(13 / 13); // Assuming always 13 columns

    // Clear existing gauge charts and title
    document.getElementById("symbols").innerHTML = "";

    // Add title above the gauge charts
    let titleDiv = document.createElement("div");
    titleDiv.classList.add("row", "mb-3");
    titleDiv.innerHTML = "<div class='col text-center' style='color: #f2f2f2; font-family: Arial, sans-serif;'><h5>Winrate by Coin</h5></div>";
    document.getElementById("symbols").appendChild(titleDiv);

    // Calculate how many symbols to center within the empty columns
    const symbolsToCenter = Math.floor(emptyColumns / 2);

    // Create two rows to contain the gauge charts
    let row1 = document.createElement("div");
    row1.classList.add("row", "justify-content-center"); // Center the content horizontally
    document.getElementById("symbols").appendChild(row1);

    let row2 = document.createElement("div");
    row2.classList.add("row", "justify-content-center"); // Center the content horizontally
    document.getElementById("symbols").appendChild(row2);

    symbols.forEach((symbol, index) => {
        let gaugeValue = seriesValues[index];
        let previousValue = previousWinRatePerSymbol[symbol] || 0; // Get previous value or default to 0 if not available
        let deltaValue = gaugeValue - previousValue; // Calculate the delta value

        // Define color thresholds based on gauge value
        let color;
        if (gaugeValue < 40) {
            color = "red";
        } else if (gaugeValue >= 40 && gaugeValue < 60) {
            color = "yellow";
        } else {
            color = "green";
        }

        let gaugeData = [{
            domain: { x: [0, 1], y: [0, 1] },
            value: gaugeValue, // Pass the numeric value
            title: { text: symbol },
            titlefont: { size: 15 },
            type: "indicator",
            mode: "gauge+number+delta",
            delta: { reference: previousValue, value: deltaValue }, // Use the delta value
            gauge: {
              threshold: { line: { color: "red", width: 20 }, thickness: 0.75, value: null },
              bar: { color: color }, // Set the color based on the threshold
              // Add axis settings
              axis: {
                range: [0, 100], // Set axis range from 0 to 100
                tickvals: [0, 25, 50, 75, 100], // Define tick values
                ticktext: ['0', '25', '50', '75', '100'], // Define tick labels without percentage symbol
                ticksuffix: '', // Remove the default percentage symbol
                visible: false // Make the axis visible
              }
            },
            number: {
              suffix: '%' // Add the percentage symbol to the displayed value
            }
          }];

        // Determine which row to append the gauge chart to
        let targetRow = index < 6 ? row1 : row2;

        // Create a new column div for each gauge chart
        let columnDiv = document.createElement("div");
        // Adjust spacing between columns
        columnDiv.classList.add("col-sm-" + columnWidth, "d-flex", "justify-content-center", "my-3"); // Added "my-3" for margin on top and bottom

        // If there are empty columns, center the symbols within them
        if (index < symbolsToCenter || index >= symbolsToCenter + numGaugeCharts) {
            columnDiv.classList.add("invisible");
        }
        columnDiv.id = symbol;

        // Append the gauge chart to the column div
        targetRow.appendChild(columnDiv);

        let layout = { 
            width: 305, 
            height: 205, 
            margin: { t: 94, b: 60, l: 60, r: 60 },
            paper_bgcolor: "transparent", 
            font: { color: "#f3f0d1", family: "Arial", size: 25 },
        };
        Plotly.newPlot(columnDiv, gaugeData, layout);
    });

    // Update the previousWinRatePerSymbol with the current values
    previousWinRatePerSymbol = { ...winRatePerSymbol };
}



// changes=================================

function createTradesTable(tradeData) {
    const tradesPerSymbol = tradeData; // Assuming tradeData is an object with symbols as keys and trade counts as values

    const symbols = Object.keys(tradesPerSymbol);
    const tradesCounts = Object.values(tradesPerSymbol);
    const totalTrades = tradesCounts.reduce((acc, count) => acc + count, 0);

    // Create an array of objects to store symbols, trade counts, and percentages
    const tradesData = symbols.map((symbol, index) => ({
        symbol,
        tradesCount: tradesCounts[index],
        percentage: (tradesCounts[index] / totalTrades) * 100
    }));

    // Sort the trades data in descending order based on trade counts
    tradesData.sort((a, b) => b.tradesCount - a.tradesCount);

    // Clear existing table content
    document.getElementById("coint-trade").innerHTML = "";

    // Add title above the table
    let titleDiv = document.createElement("div");
    titleDiv.classList.add("trades-title");
    titleDiv.innerHTML = "<h5 style='color: #f2f2f2;'>Trades by Coin</h5>";
    document.getElementById("coint-trade").appendChild(titleDiv);

    // Create a scrollable container
    let scrollContainer = document.createElement("div");
    scrollContainer.classList.add("scrollable-table-body");
    document.getElementById("coint-trade").appendChild(scrollContainer);

    // Create the table
    let table = document.createElement("table");
    table.classList.add("table", "text-center", "trades-table");
    table.style.borderRadius = "10px"; // Rounded corners
    table.style.overflow = "hidden"; // Ensure rounded corners apply to the table
    scrollContainer.appendChild(table);

    // Create the table header
    let thead = document.createElement("thead");
    let headerRow = document.createElement("tr");

    let coinHeader = document.createElement("th");
    coinHeader.innerText = "Coin";
    headerRow.appendChild(coinHeader);

    let tradesHeader = document.createElement("th");
    tradesHeader.innerText = "Trades";
    headerRow.appendChild(tradesHeader);

    let percentageHeader = document.createElement("th");
    percentageHeader.innerText = "Percentage";
    headerRow.appendChild(percentageHeader);

    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Create the table body
    let tbody = document.createElement("tbody");

    // Populate table rows with sorted data
    tradesData.forEach(({ symbol, tradesCount, percentage }) => {
        // Extract coin name (remove "_trades" and add "USDT")
        let coinName = symbol.replace("_trades", "USDT");

        // Create a row for each coin and its trades
        let row = document.createElement("tr");

        // Create the coin cell
        let coinCell = document.createElement("td");

        // Create the image element for the icon
        let img = document.createElement("img");
        img.src = `static/images/${coinName.toLowerCase()}.png`; // Adjust the path as necessary
        img.alt = coinName;
        img.classList.add("icon");

        // Append the image and text to the coin cell
        coinCell.appendChild(img);
        coinCell.appendChild(document.createTextNode(coinName));

        row.appendChild(coinCell);

        // Create the trades count cell
        let tradesCountCell = document.createElement("td");
        tradesCountCell.innerText = tradesCount;
        row.appendChild(tradesCountCell);

        // Create the percentage cell
        let percentageCell = document.createElement("td");
        percentageCell.innerText = `${percentage.toFixed(2)}%`; // Format percentage with two decimal places
        row.appendChild(percentageCell);

        tbody.appendChild(row);
    });

    table.appendChild(tbody);
    scrollContainer.appendChild(table);

    // Ensure scrollable container height for better UX
    scrollContainer.style.maxHeight = "300px"; // Adjust as needed for your layout
    scrollContainer.style.overflowY = "auto"; // Enable vertical scrolling
}

function createProfitableTable(profitData) {
    // Filter out symbols with negative profits and calculate total profit sum for positive values
    let positiveSymbols = Object.keys(profitData).filter(symbol => profitData[symbol] > 0);
    let totalPositiveProfit = positiveSymbols.reduce((acc, symbol) => acc + profitData[symbol], 0);

    // Calculate percentages for symbols with positive profits
    let symbolPercentages = positiveSymbols.map(symbol => ({
        symbol,
        profit: profitData[symbol],
        percentage: (profitData[symbol] / totalPositiveProfit) * 100
    }));

    // Sort symbolPercentages array in descending order based on percentage
    symbolPercentages.sort((a, b) => b.percentage - a.percentage);

    // Clear existing table content
    const tableContainer = document.getElementById("coint-profit");
    tableContainer.innerHTML = "";

    // Add title above the table
    let titleDiv = document.createElement("div");
    titleDiv.classList.add("trades-title");
    titleDiv.innerHTML = "<h5 style='color: #f2f2f2;'>Profit by Coin</h5>";
    tableContainer.appendChild(titleDiv);

    // Create a scrollable container
    let scrollContainer = document.createElement("div");
    scrollContainer.classList.add("scrollable-table-body");
    tableContainer.appendChild(scrollContainer);

    // Create the table
    let table = document.createElement("table");
    table.classList.add("table", "text-center", "trades-table");
    table.style.borderRadius = "10px"; // Rounded corners
    table.style.overflow = "hidden"; // Ensure rounded corners apply to the table

    // Create the table header
    let thead = document.createElement("thead");
    let headerRow = document.createElement("tr");

    let coinHeader = document.createElement("th");
    coinHeader.innerText = "Coin";
    headerRow.appendChild(coinHeader);

    let profitHeader = document.createElement("th");
    profitHeader.innerText = "Profit";
    headerRow.appendChild(profitHeader);

    let percentageHeader = document.createElement("th");
    percentageHeader.innerText = "Percentage";
    headerRow.appendChild(percentageHeader);

    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Create the table body
    let tbody = document.createElement("tbody");

    // Iterate through symbolPercentages array
    symbolPercentages.forEach(({ symbol, profit, percentage }) => {
        // Create a row for each coin and its percentage
        let row = document.createElement("tr");

        // Create the coin cell
        let coinCell = document.createElement("td");

        // Create the image element for the icon
        let img = document.createElement("img");
        img.src = `static/images/${symbol.toLowerCase()}.png`;
        img.alt = symbol;
        img.classList.add("icon");

        // Append the image and text to the coin cell
        coinCell.appendChild(img);
        coinCell.appendChild(document.createTextNode(symbol));

        row.appendChild(coinCell);

        // Create the profit cell
        let profitCell = document.createElement("td");
        profitCell.innerText = profit.toFixed(2); // Format profit with two decimal places
        row.appendChild(profitCell);

        // Create the percentage cell
        let percentageCell = document.createElement("td");
        percentageCell.innerText = `${percentage.toFixed(2)}%`; // Format percentage with two decimal places
        row.appendChild(percentageCell);

        tbody.appendChild(row);
    });

    table.appendChild(tbody);
    scrollContainer.appendChild(table);

    // Ensure scrollable container height for better UX
    scrollContainer.style.maxHeight = "300px"; // Adjust as needed for your layout
    scrollContainer.style.overflowY = "auto"; // Enable vertical scrolling
}

function createUnprofitableTable(lossData) {
    // Filter out symbols with negative profits and calculate total profit sum for negative values
    let negativeSymbols = Object.keys(lossData).filter(symbol => lossData[symbol] < 0);
    let totalNegativeProfit = negativeSymbols.reduce((acc, symbol) => acc + lossData[symbol], 0);

    // Calculate percentages for symbols with negative profits
    let symbolPercentages = negativeSymbols.map(symbol => ({
        symbol,
        profit: lossData[symbol],
        percentage: (lossData[symbol] / totalNegativeProfit) * 100
    }));

    // Sort symbolPercentages array in descending order based on percentage
    symbolPercentages.sort((a, b) => b.percentage - a.percentage);

    // Clear existing table content
    const tableContainer = document.getElementById("coint-unprofit");
    tableContainer.innerHTML = "";

    // Add title above the table
    let titleDiv = document.createElement("div");
    titleDiv.classList.add("trades-title");
    titleDiv.innerHTML = "<h5 style='color: #f2f2f2;'>Unprofitable by Coin</h5>";
    tableContainer.appendChild(titleDiv);

    // Create a scrollable container
    let scrollContainer = document.createElement("div");
    scrollContainer.classList.add("scrollable-table-body");
    tableContainer.appendChild(scrollContainer);

    // Create the table
    let table = document.createElement("table");
    table.classList.add("table", "text-center", "trades-table");
    table.style.borderRadius = "10px"; // Rounded corners
    table.style.overflow = "hidden"; // Ensure rounded corners apply to the table

    // Create the table header
    let thead = document.createElement("thead");
    let headerRow = document.createElement("tr");

    let coinHeader = document.createElement("th");
    coinHeader.innerText = "Coin";
    headerRow.appendChild(coinHeader);

    let profitHeader = document.createElement("th");
    profitHeader.innerText = "Profit";
    headerRow.appendChild(profitHeader);

    let percentageHeader = document.createElement("th");
    percentageHeader.innerText = "Percentage";
    headerRow.appendChild(percentageHeader);

    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Create the table body
    let tbody = document.createElement("tbody");

    // Iterate through symbolPercentages array
    symbolPercentages.forEach(({ symbol, profit, percentage }) => {
        // Create a row for each coin and its percentage
        let row = document.createElement("tr");

        // Create the coin cell
        let coinCell = document.createElement("td");

        // Create the image element for the icon
        let img = document.createElement("img");
        img.src = `static/images/${symbol.toLowerCase()}.png`;
        img.alt = symbol;
        img.classList.add("icon");

        // Append the image and text to the coin cell
        coinCell.appendChild(img);
        coinCell.appendChild(document.createTextNode(symbol));

        row.appendChild(coinCell);

        // Create the profit cell
        let profitCell = document.createElement("td");
        profitCell.innerText = profit.toFixed(2); // Format profit with two decimal places
        row.appendChild(profitCell);

        // Create the percentage cell
        let percentageCell = document.createElement("td");
        percentageCell.innerText = `${percentage.toFixed(2)}%`; // Format percentage with two decimal places
        row.appendChild(percentageCell);

        tbody.appendChild(row);
    });

    table.appendChild(tbody);
    scrollContainer.appendChild(table);

    // Ensure scrollable container height for better UX
    scrollContainer.style.maxHeight = "300px"; // Adjust as needed for your layout
    scrollContainer.style.overflowY = "auto"; // Enable vertical scrolling
}

function createBuySellTable(buySellData) {
    console.log("Data received for table:", buySellData);

    // Create a container for the title and table
    let container = document.getElementById('bs');
    if (container) {
        // Clear any existing content
        container.innerHTML = '';

        // Create a title element
        let title = document.createElement('div');
        title.className = 'section-title';
        title.textContent = 'Buy/Long & Sell/Short';
        title.style.color = '#f2f2f2';

        // Create a table element
        let table = document.createElement('table');
        table.className = 'table table-bordered';
        table.id = 'buySellTable';
        table.style.borderRadius = "10px"; // Rounded corners
        table.style.overflow = "hidden"; // Ensure rounded corners apply to the table

        // Center the table
        table.style.marginLeft = 'auto';
        table.style.marginRight = 'auto';

        // Check if buySellData is an object and not null
        if (typeof buySellData !== 'object' || buySellData === null) {
            console.error("Data for table is not an object or is null");
            return;
        }

        // Iterate over the keys of the buySellData object to create rows
        let rowIndex = 0;
        for (let key in buySellData) {
            if (buySellData.hasOwnProperty(key)) {
                // Create a row
                let row = document.createElement('tr');

                // Set background color based on row index
                if (rowIndex % 2 === 0) {
                    row.style.backgroundColor = '#66ff33';
                } else {
                    row.style.backgroundColor = '#ff1a1a';
                }

                // Create a cell for the key
                let keyCell = document.createElement('td');
                keyCell.textContent = key;
                keyCell.style.fontWeight = 'bold';
                row.appendChild(keyCell);

                // Create a cell for the value
                let valueCell = document.createElement('td');
                let value = buySellData[key];
                if (rowIndex < 2) {
                    valueCell.textContent = value + '%';
                } else {
                    valueCell.textContent = value;
                }
                valueCell.style.fontWeight = 'bold';
                row.appendChild(valueCell);

                // Append the row to the table
                table.appendChild(row);

                rowIndex++;
            }
        }

        // Append the title and table to the container element
        container.appendChild(title);
        container.appendChild(table);
    } else {
        console.error("Element with id 'bs' not found");
    }

    // Remove the table border
    table.style.border = 'none';
}



// Initialize chart options
var options = {
    series: [],
    chart: {
        type: 'polarArea',
        width: '400px', // Set minimum width
        height: '400px', // Set minimum height
        animations: {
            enabled: false // Disable animations for performance
        }
    },
    title: {
        text: 'Winrate by Account', // Add your title here
        align: 'center', // Align the title to the center
        margin: 20, // Space between title and chart
        offsetY: 0, // Offset from the top
        style: {
            fontSize: '18px',
            font: 'sans-serif',
            color: '#f2f2f2'
        }
    },
    labels: [],
    fill: {
        opacity: 0.8
    },
    stroke: {
        width: 1,
        colors: undefined
    },
    yaxis: {
        show: false,
        labels: {
            formatter: function(val) {
                return val + '%';
            }
        }
    },
    legend: {
        position: 'bottom'
    },
    plotOptions: {
        polarArea: {
            rings: {
                strokeWidth: 0
            },
            spokes: {
                strokeWidth: 0
            }
        }
    },
    responsive: [{
        breakpoint: 480, // Adjust breakpoints as needed
        options: {
            chart: {
                width: '100%' // Make the chart width 100% at this breakpoint
            },
            legend: {
                position: 'bottom'
            }
        }
    }]
};

// Initialize ApexCharts instance
var chart = new ApexCharts(document.querySelector("#polar-chart"), options);

// Function to capitalize series names
function capitalizeString(str) {
    return str.toUpperCase();
}

// Function to update polar chart with data
function createPolarAreaChart(winningRateData) {
    const seriesNames = Object.keys(winningRateData);
    const seriesValues = Object.values(winningRateData);
    const roundedValues = seriesValues.map(value => parseFloat(value).toFixed(2));
    const capitalizedNames = seriesNames.map(name => capitalizeString(name));
    
    chart.updateOptions({
        series: roundedValues,
        labels: capitalizedNames
    });
    
    chart.render(); // Render or update the chart after options are updated
}

// Render the chart
chart.render();


function truncateText(text, maxLength) {
    if (text.length <= maxLength) {
        return text;
    }
    return text.substring(0, maxLength) + '...';
}

$.getJSON('static/news_output/coingraphnews.json', function (response) {
    // Directly check if the response has the expected properties
    if (response && response.message) {
        const carouselInner = $('#carouselInner');

        // Extract and truncate the message
        const truncatedMessage = truncateText(response.message, 400); // Adjust max length as needed

        // Extract URLs from entities if available
        const links = response.entities.map(entity =>
            `<a href="${entity.url}" target="_blank">${response.message.substring(entity.offset, entity.offset + entity.length)}</a>`
        ).join(' | ');

        // Create the carousel item HTML
        const item = `
            <div class="carousel-item active" data-bs-interval="5000">
                <div class="d-block w-100" style="text-align: center;">
                    <div class="content" style="max-height: 400px; max-width: 350px; margin: 0 auto; color: #f2f2f2;">
                        <p>${truncatedMessage}</p>
                        <div class="read-more">${links}</div>
                    </div>
                </div>
            </div>
        `;
        carouselInner.append(item);
    } else {
        console.error("No valid data found in the JSON file or incorrect data structure.", response);
    }
}).fail(function (jqXHR, textStatus, errorThrown) {
    console.error("Failed to load the JSON file:", textStatus, errorThrown);
});

// Ensure your carousel structure is correct and the buttons are within the carousel container


    // Exporting the functions

    $(document).ready(function () {
        ctx1 = document.getElementById('cumulativeLineChart1');
        ctx2 = document.getElementById('cumulativeBarChart2');
});

// function updateSize() {
//     document.getElementById('width').textContent = window.innerWidth;
//     document.getElementById('height').textContent = window.innerHeight;
//   }

  // Initial call to set initial values
//   updateSize();

  // Event listener for window resize
//   window.addEventListener('resize', updateSize);

// refreshData();

// this is api/initial_data/
// export function startDataRefresh() {
//     setInterval(async () => {
//         await Promise.all([livedata_metrics()]);
//         // console.log("livedata_metrics")

//     }, 10000); // 10000 milliseconds = 2 minutes
// }
// startDataRefresh();






export { updateCharts, refreshData , fetch_data};
