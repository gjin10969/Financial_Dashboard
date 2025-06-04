// Import statements
import { refreshData, livedata_metrics, allAccountData } from './index.js';
// import { refreshDashboard } from './dashboard.js';
// import { updateAccountMetrics, updateFilteredData } from './navigation.js';
import { updateFilteredData } from './navigation.js';
// import { cancel_request_data } from './api.js';

// Get references to the spinner
let fullPageSpinner = $('#fullPageSpinner');

export async function showSpinner() {
    console.log('showSpinner called'); // Debug statement
    fullPageSpinner.removeClass('d-none');
    console.log('Spinner visibility after show:', fullPageSpinner.is(':visible')); // Check visibility
}

export async function hideSpinner() {
    console.log('hideSpinner called'); // Debug statement
    fullPageSpinner.addClass('d-none');
    console.log('Spinner visibility after hide:', fullPageSpinner.is(':visible')); // Check visibility
}


        // Global variable to store the checked values
        let checkedValues = [];

        // Function to update the all_Accounts flag based on selected checkboxes
        function updateAllAccountsFlag() {
            // Update checked values
            updateCheckedValues();

            // Check if only mirrorxtotal is checked
            if (checkedValues.length === 1 && checkedValues.includes('mirrorxtotal')) {
                window.all_Accounts = true;
            } else {
                window.all_Accounts = false;
            }

            console.log('all_Accounts:', window.all_Accounts); // Debug statement
        }

        // Function to update the checkedValues variable
        function updateCheckedValues() {
            // Get all checked checkboxes with id account_check
            checkedValues = $('input[id="account_check"]:checked').map(function () {
                return $(this).val();
            }).get();

            console.log('Checked Values:', checkedValues); // Debug statement
        }

        // Add an onclick event handler for checkboxes with id account_check
        $('input[id="account_check"]').on('click', function () {
            updateAllAccountsFlag();
        });

async function get_filtered_main() {
    // Event listener for button clicks
    $(".resbat").click(async function() {
        // Remove 'active' class from all buttons
        $(".resbat").removeClass("active");
        // Add 'active' class to the clicked button
        $(this).addClass("active");
        // Store the clicked button's ID in the variable
        let selectedFilter = $(this).attr("id");
        console.log(selectedFilter)

        // AJAX request
        try {
            await showSpinner();
            let response;
            if (selectedFilter === "seven") {
                response = await $.ajax({
                    url: `/api/date_pages?date_range=last_7_days&mirror_accounts=${checkedValues}`,
                    type: 'GET'
                });
            } else if (selectedFilter === "three") {
                response = await $.ajax({
                    url: `/api/date_pages?date_range=last_3_months&mirror_accounts=${checkedValues}`,
                    type: 'GET'
                });
            } else if (selectedFilter === "one") {
                response = await $.ajax({
                    url: `/api/date_pages?date_range=last_30_days&mirror_accounts=${checkedValues}`,
                    type: 'GET'
                });
            } else if (selectedFilter === "year") {
                response = await $.ajax({
                    url: `/api/date_pages?date_range=last_1_year&mirror_accounts=${checkedValues}`,
                    type: 'GET'
                });
            }
            // Handle response
            console.log("success", response);



        } catch (error) {
            console.error("Error:", error);
        } finally {
            await updatedataonrefresh();
            await new Promise(resolve => setTimeout(resolve, 2000));
            await hideSpinner();
        }
    });
}

        // Get the current date
        let currentDate = new Date();

        // Get the first day of the current month
        let firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() - 6, 1);
        console.log(firstDayOfMonth)

        // Format the dates to YYYY-MM-DD
        let formatDate = (date) => {
            let month = ('0' + (date.getMonth() + 1)).slice(-2);
            let day = ('0' + date.getDate()).slice(-2);
            return date.getFullYear() + '-' + month + '-' + day;
        };

        // Set the default values
        $('#date-range-form #start').val(formatDate(firstDayOfMonth));
        $('#date-range-form #end').val(formatDate(currentDate));

        window.filtered_activated = false;
        window.all_Accounts = false;

        // Click event handler for date filter button
        $("#date_filter").on('click', async function() {
            // Check if 'ALL ACCOUNTS' is selected
            if (window.all_Accounts) {
                // Call the refreshData function and stop further execution
                allAccountData();
                return;
            }
        
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
        
            // Collect the values of checked checkboxes for coins
            let checkedCoins = [];
            let coins_list = 'UNIUSDT,AVAXUSDT,LINKUSDT,XRPUSDT,ETHUSDT,BNBUSDT,SOLUSDT,ATOMUSDT,LTCUSDT,MATICUSDT,ADAUSDT,BTCUSDT,DOTUSDT';
        
            // Check if 'ALL' is selected for coins
            $('input[id="symbol_check"]:checked').each(function() {
                if ($(this).val() === 'ALL') {
                    checkedCoins = coins_list.split(','); // Select all coins
                } else {
                    checkedCoins.push($(this).val());
                }
            });
        
            // Collect the values of checked checkboxes for accounts
            let checkedAccounts = [];
            let accounts_list = "mirrorxtotal";
        
            // Check if 'ALL' is selected for accounts
            $('input[id="account_check"]:checked').each(function() {
                if ($(this).val() === 'mirrorxtotal') {
                    checkedAccounts = accounts_list.split(','); // Select all accounts
                } else {
                    checkedAccounts.push($(this).val());
                }
            });
        
            // Convert arrays to comma-separated strings
            let checkedCoinsStr = checkedCoins.join(',');
            let checkedAccountsStr = checkedAccounts.join(',');
        
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
        
                window.filtered_activated = true;
        
                console.log('filtered_activated', window.filtered_activated);
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

const updateRealTimeDate = async () => {
    let success = false;
    try {
        // Set a timeout for the whole operation
        const timeoutPromise = new Promise((resolve, reject) => {
            setTimeout(() => reject(new Error('Timeout occurred')), 10000); // Adjust timeout as needed
        });

        // Execute all promises concurrently with Promise.race
        // await Promise.all([livedata_metrics()])
        await Promise.race([
            Promise.all([
                // updateAccountMetrics(),
                updateFilteredData(),
                refreshData(),
                // refreshDashboard(),
            ]),
            timeoutPromise
        ]);
        
        success = true;
    } catch (error) {
        console.error('Error updating real-time data:', error);
        // Optionally, you can display an error message here using Swal.fire() or handle the error in another way.
    } finally {
        if (success) {
            Swal.fire({
                icon: "success",
                title: 'Data Successfully loaded!'
            });
        }
        // Optionally, you can close any loading indicator here if needed.
        Swal.close();
    }
};



const updatedataonrefresh = async () => {
    await showSpinner();
    await Promise.all([updateFilteredData(), refreshData()]);
    // await Promise.all([refreshDashboard()]);
    await new Promise(resolve => setTimeout(resolve, 1000));
    await hideSpinner();
};
livedata_metrics();
updatedataonrefresh();

$(document).ready(async function() {
    await get_filtered_main();
});

export { get_filtered_main };

// Click event handler for download report button
$("#download_report").on('click', async function() {
    // Disable the button
    $(this).prop('disabled', true);

    // Show loading popup
    Swal.fire({
        title: 'Generating report, please wait.',
        text: 'This may take a moment...',
        icon: 'info',
        showConfirmButton: false,
        allowOutsideClick: false,
        customClass: {
            popup: 'custom-Swal-fire-popup',
        }
    });

    try {
        const response = await $.ajax({
            url: '/api/generate_pdf',
            method: 'GET',
            xhrFields: {
                responseType: 'blob'
            }
        });
        var blob = new Blob([response], { type: 'application/pdf' });
        var url = window.URL.createObjectURL(blob);
        var a = document.createElement('a');
        // Getting the current date
        var today = new Date();
        var day = String(today.getDate()).padStart(2, '0');
        var month = String(today.getMonth() + 1).padStart(2, '0'); // January is 0!
        var year = today.getFullYear();
        var formattedDate = year + '-' + month + '-' + day;
        a.style.display = 'none';
        a.href = url;
        a.download = `Dashboard-report_${formattedDate}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);

        Swal.close();
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: "error",
            title: 'Something went wrong, please try again.'
        });
    } finally {
        // Enable the button
        $(this).prop('disabled', false);
    }
});