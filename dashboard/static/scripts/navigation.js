let previousTotalBalance = null;

export async function updateAccountMetrics(navigationData) {
    try {
        if (navigationData && navigationData.overall) {
            let names = window.checkedAccountsStr ? window.checkedAccountsStr.toUpperCase().split(',') : ["MIRRORXTOTAL"];
            const accountMetrics = navigationData.account_metrics;
            console.log(accountMetrics);
            console.log('window.checkedAccountsStr', names);

            let totalBalance = 0;
            let totalReturn = 0;
            let unrealizedPNL = 0;
            let profitDollarData = 0;

            names.forEach(name => {
                if (accountMetrics.total_balance_data[name] !== undefined) {
                    totalBalance += accountMetrics.total_balance_data[name];
                    totalReturn += accountMetrics.total_return_data[name];
                    unrealizedPNL += accountMetrics.total_unrealized_pnl_data[name];
                    profitDollarData += accountMetrics.profit_dollar_data[name];
                }
            });

            let roundedTotalBalance = totalBalance < 0 ? '-$' + Math.abs(totalBalance).toFixed(2) : '$' + totalBalance.toFixed(2);
            let roundedAccountReturn = totalReturn < 0 ? '-' + Math.abs(totalReturn).toFixed(2) + '%' : totalReturn.toFixed(2) + '%';
            let newPrice = unrealizedPNL < 0 ? '-$' + Math.abs(unrealizedPNL).toFixed(3) : '$' + unrealizedPNL.toFixed(3);

            let tfValueElement = $("#unrealized-pnl");
            let currentPrice = parseFloat(tfValueElement.text().replace('$', '').replace(',', ''));

            let colorPNL = getColorAndArrow(unrealizedPNL).color;
            tfValueElement.text(newPrice).css('color', colorPNL);

            let arrowBalance = previousTotalBalance !== null && totalBalance > previousTotalBalance ? '↑' : '↓';
            $("#total-balance").text(roundedTotalBalance).append(" " + arrowBalance);

            let colorAndArrowReturn = getColorAndArrow(totalReturn);
            $("#return").text(roundedAccountReturn).css('color', colorAndArrowReturn.color).append(" " + colorAndArrowReturn.arrow);

            if (profitDollarData < 0) {
                $(`#total-realizedPnl`).text('-$' + Math.abs(profitDollarData.toFixed(2))).css('color', getColorAndArrow(profitDollarData).color).append(" " + getColorAndArrow(profitDollarData).arrow);
            }
            else {
                $(`#total-realizedPnl`).text('$' + profitDollarData.toFixed(2)).css('color', getColorAndArrow(profitDollarData).color).append(" " + getColorAndArrow(profitDollarData).arrow);
            }
            tfValueElement.data("lastprice", parseFloat(unrealizedPNL));

            // Store the current total balance for the next comparison
            previousTotalBalance = totalBalance;
        }
    } catch (error) {
        console.error('Error updating account metrics:', error);
        // Handle the error, you can show a message to the user or retry the request
    }
}

function getColorAndArrow(value) {
    if (parseFloat(value) < 0) {
        return { color: 'red', arrow: '↓' }; // Arrow down for negative values
    } else {
        return { color: 'green', arrow: '↑' }; // Arrow up for non-negative (including zero) values
    }
}




export async function updateFilteredData(navigationData) {
    // console.log("data",data)

    try {
        if (navigationData && navigationData.response_data) { // Check if data and response_data are defined

            const accountData = navigationData.response_data;
            console.log(accountData);
            // Process filtered data
            // let total_realized_pnl = 0;
            let total_trading_days = 0;
            let total_winning_days = 0;
            let total_trades = 0;
            // let total_winning_trades = 0;
            let total_winning_rate = 0;
            let max_draw_down_sum = 0;
            let total_fees = 0;

            // total_winning_trades += accountData.winning_trades.length;

            // Accumulate other values
            // total_realized_pnl += accountData.total_realized_pnl;
            // console.log(total_realized_pnl);
            total_trading_days = accountData.trading_days;
            total_winning_days = accountData.winning_days;
            total_trades += data.overall.total_trades;
            total_winning_rate += data.overall.overall_winrate;
            max_draw_down_sum += accountData.max_draw;
            total_fees += accountData.total_fees;

            // Display the accumulated values
            // if (total_realized_pnl < 0) {
            //     $(`#total-realizedPnl`).text('-$' + Math.abs(total_realized_pnl.toFixed(2))).css('color', getColorAndArrow(total_realized_pnl).color).append(" " + getColorAndArrow(total_realized_pnl).arrow);
            // }
            // else {
            //     $(`#total-realizedPnl`).text('$' + total_realized_pnl.toFixed(2)).css('color', getColorAndArrow(total_realized_pnl).color).append(" " + getColorAndArrow(total_realized_pnl).arrow);
            // }
            $(`#trading-days-value`).text(total_trading_days);
            $(`#winning-days`).text(total_winning_days).append(" " + getColorAndArrow(total_winning_days).arrow);
            $(`#total-trades`).text(total_trades);
            // $(`#winning-trades`).text(total_winning_trades).css('color', getColorAndArrow(total_winning_trades).color).append(" " + getColorAndArrow(total_winning_trades).arrow);
            $("#win_rate").text(total_winning_rate.toFixed(2)+'%').append(" " + getColorAndArrow(total_winning_rate).arrow);
            if (max_draw_down_sum < 0){
                $('#max-draw-down').text('-' + Math.abs(max_draw_down_sum.toFixed(3)) + '%');

            }
            else {
                $(`#max-draw-down`).text( (max_draw_down_sum.toFixed(3) ) + '%');
            }
            if (total_fees < 0){
                $(`#total-fees`).text('-$' + total_fees.toFixed(2));
            }
            else {
                $(`#total-fees`).text('-$' + total_fees.toFixed(2));
            }
            // Continue processing other filtered data as needed
        }
    } catch (error) {
        console.error('Error updating filtered data:', error);
        // Handle the error, you can show a message to the user or retry the request
    }
}