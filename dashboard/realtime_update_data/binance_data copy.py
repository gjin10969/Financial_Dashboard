const express = require('express');
const { Binance } = require('@binance/connector');

const router = express.Router();

// Initial balances and account configuration
const accounts = [
    "your_account",
    "your_account",
    "your_account",
    "your_account",
    "your_account",
    "your_account",
];

// Dictionary to store the client instances for each account
const clients = {};
for (const acc of accounts) {
    const secret = process.env[`${acc}_secret`];
    const key = process.env[`${acc}_key`];
    if (secret && key) {
        const client = new Binance().setApiKey(key).setApiSecret(secret);
        clients[acc] = client;
    }
}

// Function to get total wallet balance for a Binance client
const walletBalance = async (client) => {
    try {
        const walletAccount = await client.futuresAccount(); // Use the correct method here
        const totalBalance = parseFloat(walletAccount.totalWalletBalance) + parseFloat(walletAccount.totalUnrealizedProfit);
        return totalBalance;
    } catch (error) {
        console.error('Error fetching wallet balance:', error);
        return 0; // Return a default value or handle the error accordingly
    }
};

// Define the endpoint to fetch wallet balances
router.get('/balances', async (req, res) => {
    const balances = {};
    for (const acc of accounts) {
        if (clients[acc]) {
            balances[acc] = await walletBalance(clients[acc]);
        } else {
            balances[acc] = 'Client not initialized';
        }
    }
    res.json(balances);
});

module.exports = router;
