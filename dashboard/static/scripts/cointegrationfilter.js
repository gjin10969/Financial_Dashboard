// import { getCointData } from "./cointegration-navigation";

// Get the current date
let currentDate = new Date();

// Get the first day of the current month
let firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);

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

$("#coint_filter").on('click', async function() {
    
})