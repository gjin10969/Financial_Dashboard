$(document).ready(function() {

// Call the fetch function when the page is ready
fetchBacktestData();

function fetchBacktestData() {
    $.ajax({
        url: '/api/get_backtest_data', // Your API endpoint
        method: 'GET',
        dataType: 'json',
        success: function (data) {
            // Check if the data is an array
            if (Array.isArray(data) && data.length > 0) {
                // Clear the existing data in the table body
                $('#backtest_data_body').empty();

                // Loop through each item in the data array
                data.forEach(function (item) {
                    // Create a new row for each item
                    const row = `
                        <tr>
                            <td>${item.id || 'N/A'}</td>
                            <td>${item.symbol || 'N/A'}</td>
                            <td>${item.ver || 'N/A'}</td>
                            <td>${item.interval || 'N/A'}</td>
                            <td>${item.trade_start || 'N/A'}</td>
                            <td>${item.trade_end || 'N/A'}</td>
                            <td>${item.datetoday || 'N/A'}</td>
                            <td><button class="btn btn-info" data-id="${item.id}" data-symbol="${item.symbol}" data-backtest-price="${item.backtestPrice}" data-backtest-quantity="${item.backtestQuantity}" data-backtest-pnl="${item.backtestPnl}" data-livetrade-price="${item.livetradePrice}" data-livetrade-quantity="${item.livetradeQuantity}" data-livetrade-pnl="${item.livetradePnl}" data-bs-toggle="modal" data-bs-target="#files-modal">Files</button></td>
                        </tr>
                    `;
                    // Append the new row to the table body
                    $('#backtest_data_body').append(row);
                });

                // Initialize DataTable
                if ($.fn.DataTable.isDataTable('#data-table')) {
                    $('#data-table').DataTable().destroy();
                }
                $('#data-table').DataTable();

                // Add event listener to populate modal content when a button is clicked
                $('#data-table').on('click', 'button', function () {
                    const button = $(this);
                    const id = button.data('id');
                    const symbol = button.data('symbol');
                    const backtestPrice = button.data('backtest-price');
                    const backtestQuantity = button.data('backtest-quantity');
                    const backtestPnl = button.data('backtest-pnl');
                    const livetradePrice = button.data('livetrade-price');
                    const livetradeQuantity = button.data('livetrade-quantity');
                    const livetradePnl = button.data('livetrade-pnl');

                    // Populate the modal with data
                    $('#Modal .modal-body').find('#modal-backtest-table tbody').html(`
                        <tr>
                            <td>${backtestPrice}</td>
                            <td>${backtestQuantity}</td>
                            <td>${backtestPnl}</td>
                        </tr>
                    `);
                    $('#Modal .modal-body').find('#modal-livetrade-table tbody').html(`
                        <tr>
                            <td>${livetradePrice}</td>
                            <td>${livetradeQuantity}</td>
                            <td>${livetradePnl}</td>
                        </tr>
                    `);
                });

            } else {
                // Handle empty or unexpected data
                $('#backtest_data_body').html('<tr><td colspan="8" class="empty-message">No data available</td></tr>');
            }
        },
        error: function (xhr, status, error) {
            console.error('Error fetching data:', error);
            // Display error message if fetching fails
            $('#backtest_data_body').html('<tr><td colspan="8" class="empty-message">Error fetching data</td></tr>');
        }
    });
}


// Click event handler for date filter button
$("#backtest_button").on('click', async function() {

    // Get start and end dates
    let startDate = $('#backtest_start').val();
    let endDate = $('#backtest_end').val(); // Changed from 'backtest_start' to 'backtest_end'
    // Use name attributes to select checkboxes
    let symbol = $('input[name="form_symbol"]:checked');
    let model = $('input[name="form_model"]:checked');
    let interval = $('input[name="form_interval"]:checked');

    // Check if any required fields are empty
    if (symbol.length === 0) {
        return Swal.fire({
            title: 'Kindly check a symbol field',
            icon: 'warning',
            showConfirmButton: true,
            allowOutsideClick: true,
            customClass: {
                popup: 'custom-Swal.fire-popup',
            }
        });
    }

    // Check if any required fields are empty
    if (model.length === 0) {
        return Swal.fire({
            title: 'Kindly check a model field',
            icon: 'warning',
            showConfirmButton: true,
            allowOutsideClick: true,
            customClass: {
                popup: 'custom-Swal.fire-popup',
            }
        });
    }

    // Check if any required fields are empty
    if (interval.length === 0) {
        return Swal.fire({
            title: 'Kindly check an interval field',
            icon: 'warning',
            showConfirmButton: true,
            allowOutsideClick: true,
            customClass: {
                popup: 'custom-Swal.fire-popup',
            }
        });
    }

    // Check if any required fields are empty
    if (startDate == "") {
        return Swal.fire({
            title: 'Kindly input a start date',
            icon: 'warning',
            showConfirmButton: true,
            allowOutsideClick: true,
            customClass: {
                popup: 'custom-Swal.fire-popup',
            }
        });
    }

    // Check if any required fields are empty
    if (endDate == "") {
        return Swal.fire({
            title: 'Kindly input an end date',
            icon: 'warning',
            showConfirmButton: true,
            allowOutsideClick: true,
            customClass: {
                popup: 'custom-Swal.fire-popup',
            }
        });
    }

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
        // Disable the button
        $(this).prop('disabled', true);

            // Collect the values of checked checkboxes for coins
            let checkedSymbol = [];
            let symbol_list = 'UNIUSDT,AVAXUSDT,LINKUSDT,XRPUSDT,ETHUSDT,BNBUSDT,SOLUSDT,ATOMUSDT,LTCUSDT,MATICUSDT,ADAUSDT,BTCUSDT,DOTUSDT';
        
            // Check the checkedSymbol if ALL or not
            $('input[id="symbol_backtest"]:checked').each(function() {
                if ($(this).val() === 'ALL') {
                    checkedSymbol = symbol_list.split(','); // Convert symbol_list to an array
                    return false; // Exit the loop once 'ALL' is found
                } else {
                    checkedSymbol.push($(this).val());
                }
            });
        
            // Collect the values of checked checkboxes for models
            let checkedModel = [];
            let accounts_list = 'P0201,P0202,P0301,P0302,P0401,P0402,P0501,P0502';
        
            // Check the checkedModel if ALL or not
            $('input[id="model_backtest"]:checked').each(function() {
                if ($(this).val() === 'ALL') {
                    checkedModel = accounts_list.split(','); // Convert accounts_list to an array
                    return false; // Exit the loop once 'ALL' is found
                } else {
                    checkedModel.push($(this).val());
                }
            });
        
            // Collect the values of checked checkboxes for intervals
            let checkedInterval = [];
            let interval_list = '1m,1H,4H,1D,1M,3M,1Y';
        
            // Check the checkedInterval if ALL or not
            $('input[id="interval_backtest"]:checked').each(function() {
                if ($(this).val() === 'ALL') {
                    checkedInterval = interval_list.split(','); // Convert interval_list to an array
                    return false; // Exit the loop once 'ALL' is found
                } else {
                    checkedInterval.push($(this).val());
                }
            });
        
            // Convert arrays to comma-separated strings
            let checkedSymbolStr = checkedSymbol.join(',');
            let checkedModelStr = checkedModel.join(',');
            let checkedIntervalStr = checkedInterval.join(',');
        
            console.log(checkedModelStr);
            console.log(checkedSymbolStr);
            console.log(checkedIntervalStr);

        // Show loading popup
        // Swal.fire({
        //     title: 'Backtesting data, please wait.',
        //     text: 'This may take a while...',
        //     icon: 'info',
        //     showConfirmButton: false,
        //     allowOutsideClick: false,
        //     customClass: {
        //         popup: 'custom-Swal.fire-popup',
        //     }
        // });
    

    try {
        var backtest_loader = '<div class="backtest_loader"><img src="../static/images/backtest.gif" viewBox="0 0 140 140" width="140" height="140">';
        // First AJAX request to '/api/items_post'
        const postResponse = await $.ajax({
            url: '/api/items_post',
            type: 'POST',
            data: {
                symbol: checkedSymbolStr,
                ver: checkedModelStr,
                interval: checkedIntervalStr,
                trade_start: startDate,
                trade_end: endDate
            }
        });
        console.log(postResponse);
        console.log('Post request succeeded');

        // Second AJAX request to '/api/item_get'
        const getResponse = await $.ajax({
            url: '/api/item_get',
            type: 'GET',
            beforeSend: function() {
                swal.fire({
                    html: '<h5>Backtesting...</h5>',
                    showConfirmButton: false,
                    allowOutsideClick: false,
                    didRender: function() {
                         // there will only ever be one sweet alert open.
                         $('.swal2-content').prepend(backtest_loader);
                    }
                });
            },
        });
        console.log(getResponse);
        console.log('Get request succeeded');

        // Assume getResponse is the object you get from the response
        if (getResponse && getResponse.generated_files) {
            // Clear previous results if any
            $("#generated_files_container").empty();
            console.log(getResponse.generated_files);

            getResponse.generated_files.forEach(file => {
                console.log(`Generated file: ${file}`);

                // Determine the type of file (image or CSV)
                if (file.endsWith(".png")) {
                    // Create an image element for PNG files
                    $("#generated_files_container").append(`
                        <div class="file-item">
                            <img src="${file}" alt="Generated Image" class="img-fluid">
                        </div>
                    `);
                } else if (file.endsWith(".csv")) {
                    // Create a link element for CSV files
                    $("#generated_files_container").append(`
                        <div class="file-item">
                            <a href="${file}" download>Download ${file.split('/').pop()}</a>
                        </div>
                    `);
                }
            });

            // Hide the backtest modal and show the generated files modal
            var backtestModal = bootstrap.Modal.getInstance(document.getElementById('backtestModal'));
            var generatedModal = new bootstrap.Modal(document.getElementById('generatedModal'));
            
            if (backtestModal) {
                backtestModal.hide();
            }
            
            generatedModal.show();
        } else {
            console.warn('No files were generated.');
        }


    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: "error",
            title: 'An error occurred while processing your request. Please try again later.'
        });
    } finally {
        Swal.fire({
            icon: "success",
            title: 'Backtest completed! Kindly check the generated files.'
        });
        // Enable the button
        $(this).prop('disabled', false);
        fetchBacktestData();
    }
});

$("download_history").on('click', async function () {


})

});