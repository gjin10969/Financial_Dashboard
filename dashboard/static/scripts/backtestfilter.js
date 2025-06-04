// Click event handler for date filter button
$("#date_filter").on('click', async function() {
    // Disable the button
    $(this).prop('disabled', true);

    // Get start and end dates
    let startDate = $('#date-range-form #start').val();
    let endDate = $('#date-range-form #end').val();

    // Check if start date is higher than end date
    if (startDate > endDate) {
        // Enable the button
        $(this).prop('disabled', false);
        return Swal.fire({
            icon: "warning",
            title: 'The "From" date should not be higher than the "To" date.',
            closeOnClickOutside: false
        });
    } 

    // Show loading popup
    Swal.fire({
        title: 'Processing data, please wait.',
        text: 'This may take a moment...',
        icon: 'info',
        showConfirmButton: false,
        allowOutsideClick: false,
        customClass: {
            popup: 'custom-Swal.fire-popup',
        }
    });

    // let getALLCoinsValue = $('#coin-filter').val();
    // console.log("getALLCoinsValue", getALLCoinsValue)

    // Collect the values of checked checkboxes for coins
    let checkedCoins = [];
    let coins_list = 'UNIUSDT,AVAXUSDT,LINKUSDT,XRPUSDT,ETHUSDT,BNBUSDT,SOLUSDT,ATOMUSDT,LTCUSDT,MATICUSDT,ADAUSDT,BTCUSDT,DOTUSDT';

    // Check the checkedCoins if ALL or not
    $('input[id="symbol_check"]:checked').each(function() {
        if ($(this).val() === 'ALL') {
            checkedCoins = coins_list.split(','); // Convert coins_list to an array
            return false; // Exit the loop once 'ALL' is found
        } else {
            checkedCoins.push($(this).val());
        }
    });

    // Collect the values of checked checkboxes for coins
    let checkedAccounts = [];
    let accounts_list = 'mirrorx1,mirrorx2,mirrorx3,mirrorx4,mirrorx5,mirrorxfund,team';

    // Check the checkedCoins if ALL or not
    $('input[id="account_check"]:checked').each(function() {
        if ($(this).val() === 'mirrorxtotal') {
            checkedAccounts = accounts_list.split(','); // Convert coins_list to an array
            return false; // Exit the loop once 'ALL' is found
        } else {
            checkedAccounts.push($(this).val());
        }
    });

    // Convert arrays to comma-separated strings
    // Check if all coins are selected
    let checkedCoinsStr = checkedCoins.join(',');

    let checkedAccountsStr = checkedAccounts.join(',');

    console.log("checkedAccountsStr",checkedAccountsStr);
    console.log(checkedCoinsStr);

    // console.log(checkedAccount);
    console.log(startDate);
    console.log(endDate);
    // console.log(checkedCoin);

    // let coins_list = 'UNIUSDT,AVAUSDT,LINKUSDT,XRPUSDT,ETHUSDT,BNBUSDT,SOLUSDT,ATOMUSDT,LTCUSDT,MATICUSDT,ADAUSDT,BTCUSDT';
    // if (checkedCoin === 'ALL') {
    //     checkedCoin = coins_list;
    //     console.log('checkedCoin', coins_list)
    // }

    // Make an AJAX request to the Django server with date parameters
    try {
        const response = await $.ajax({
            url: '/api/post_filtered',
            type: 'POST',
            data: {
                mirror_accounts: checkedAccountsStr,
                start_date: startDate,
                end_date: endDate,
                symbols: checkedCoinsStr
            }
        });
        console.log(response);
        console.log('Success');
        $("#last-updated").text(new Date().toLocaleString());
        await updateRealTimeDate();
        livedata_metrics();

    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: "error",
            title: 'No data available for the selected date. Please try again later.'
        });
    } finally {
        $(this).prop('disabled', false);
    }
});