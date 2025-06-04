
let cancelController = new AbortController();

// Function to cancel the fetch request
export async function cancel_request_data() {
    cancelController.abort();
}

// Function to fetch data
async function fetch_data() {
    try {
        const response = await fetch('/api/get_filtered_data', {
            method: 'GET',
            signal: cancelController.signal // Pass the signal to the fetch request
        });
        return response.json(); // Return the response
    } catch (error) {
        console.error('Error fetching data:', error);
        throw error; // Throw the error so it can be caught by the caller
    }
}


async function initial_load() {
    try {
        const response = await $.ajax({
            url: '/api/initial_load',
            type: 'GET'
        });
        // console.log("response", response)
        return response; // Return the response
    } catch (error) {
        console.error('Error fetching data:', error);
        throw error; // Throw the error so it can be caught by the caller
    }
}

async function get_coint_data() {
    try {
        const response = await $.ajax({
            url: '/api/getCointData',
            type: 'GET'
        });

        return response;
    } catch (error) {
        console.error('Error fetching combined data:', error);
        throw error;
    }
}


export {fetch_data, initial_load, get_coint_data};