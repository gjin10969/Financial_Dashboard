export async function updateNavigationData1(navigationData) {
    try {
            // Get account account to check (default to ["ALL"] if none selected)
            let accounts = window.checkedAccountsStr ? window.checkedAccountsStr.toUpperCase().split(',') : ["ALL"];
            console.log(navigationData);
            console.log('window.checkedAccountsStr', accounts);

            let totalBalance = 0;
            let totalReturn = 0;
            let unrealizedPNL = 0;
            let profitDollarData = 0;

            totalBalance += navigationData.Total_Balance;
            totalReturn += navigationData.Return;
            unrealizedPNL += navigationData.Unrealized_PnL;
            profitDollarData += navigationData.Total_Realized_Pnl;

            // Format the output values
            let roundedTotalBalance = totalBalance < 0 ? '-$' + Math.abs(totalBalance).toFixed(2) : '$' + totalBalance.toFixed(2);
            let roundedAccountReturn = totalReturn < 0 ? '-' + Math.abs(totalReturn).toFixed(2) + '%' : totalReturn.toFixed(2) + '%';
            let newPrice = unrealizedPNL < 0 ? '-$' + Math.abs(unrealizedPNL).toFixed(3) : '$' + unrealizedPNL.toFixed(3);

            // Update the UI with the new values
            $("#cointegration-unrealized-pnl").text(newPrice).css('color', getColorAndArrow(unrealizedPNL).color);
            
            // Arrow for total balance
            // let arrowBalance = previousTotalBalance !== null && totalBalance > previousTotalBalance ? '↑' : '↓';
            $("#cointegration-total-balance").text(roundedTotalBalance);

            // Update return metrics
            let colorAndArrowReturn = getColorAndArrow(totalReturn);
            $("#cointegration-return").text(roundedAccountReturn).css('color', colorAndArrowReturn.color).append(" " + colorAndArrowReturn.arrow);

            // Update realized PnL
            if (profitDollarData < 0) {
                $(`#cointegration-total-realizedPnl`).text('-$' + Math.abs(profitDollarData.toFixed(2))).css('color', getColorAndArrow(profitDollarData).color).append(" " + getColorAndArrow(profitDollarData).arrow);
            } else {
                $(`#cointegration-total-realizedPnl`).text('$' + profitDollarData.toFixed(2)).css('color', getColorAndArrow(profitDollarData).color).append(" " + getColorAndArrow(profitDollarData).arrow);
            }
            $("#cointegration-unrealized-pnl").data("lastprice", parseFloat(unrealizedPNL));

            // Store the current total balance for the next comparison
            // previousTotalBalance = totalBalance;

    } catch (error) {
        console.error('Error updating account metrics:', error);
        // Handle the error, you can show a message to the user or retry the request
    }
}

// Function to determine the color and arrow based on value
function getColorAndArrow(value) {
    if (parseFloat(value) < 0) {
        return { color: 'red', arrow: '↓' }; // Arrow down for negative values
    } else {
        return { color: 'green', arrow: '↑' }; // Arrow up for non-negative (including zero) values
    }
}


export async function updateNavigationData2(navigationData) {
    // console.log("data",data)

    try {
            console.log(navigationData);
            // Process filtered data
            // let total_realized_pnl = 0;
            let total_trading_days = 0;
            let total_winning_days = 0;
            let total_trades = 0;
            // let total_winning_trades = 0;
            let total_winning_rate = 0;
            let max_draw_down_sum = 0;
            let total_fees = 0;

            // total_winning_trades += navigationData.winning_trades.length;

            // Accumulate other values
            // total_realized_pnl += navigationData.total_realized_pnl;
            // console.log(total_realized_pnl);
            total_trading_days = navigationData.Trading_Days;
            total_winning_days = navigationData.Winning_Days;
            total_trades += navigationData.Total_Trades;
            total_winning_rate += navigationData.Win_Rate;
            max_draw_down_sum += navigationData.Max_Drawdown;
            total_fees += navigationData.Total_Fees;

            // Display the accumulated values
            // if (total_realized_pnl < 0) {
            //     $(`#total-realizedPnl`).text('-$' + Math.abs(total_realized_pnl.toFixed(2))).css('color', getColorAndArrow(total_realized_pnl).color).append(" " + getColorAndArrow(total_realized_pnl).arrow);
            // }
            // else {
            //     $(`#total-realizedPnl`).text('$' + total_realized_pnl.toFixed(2)).css('color', getColorAndArrow(total_realized_pnl).color).append(" " + getColorAndArrow(total_realized_pnl).arrow);
            // }
            $(`#cointegration-trading-days-value`).text(total_trading_days);
            $(`#cointegration-winning-days`).text(total_winning_days).append(" " + getColorAndArrow(total_winning_days).arrow);
            $(`#cointegration-total-trades`).text(total_trades);
            // $(`#winning-trades`).text(total_winning_trades).css('color', getColorAndArrow(total_winning_trades).color).append(" " + getColorAndArrow(total_winning_trades).arrow);
            $("#cointegration-win-rate").text(total_winning_rate.toFixed(2)+'%').append(" " + getColorAndArrow(total_winning_rate).arrow);
            if (max_draw_down_sum < 0){
                $('#cointegration-max-draw-down').text('-' + Math.abs(max_draw_down_sum.toFixed(3)) + '%');

            }
            else {
                $(`#cointegration-max-draw-down`).text( (max_draw_down_sum.toFixed(3) ) + '%');
            }
            if (total_fees < 0){
                $(`#cointegration-total-fees`).text('-$' + total_fees.toFixed(2));
            }
            else {
                $(`#cointegration-total-fees`).text('-$' + total_fees.toFixed(2));
            }
            // Continue processing other filtered data as needed
    } catch (error) {
        console.error('Error updating filtered data:', error);
        // Handle the error, you can show a message to the user or retry the request
    }
}