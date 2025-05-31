// Dashboard Demo JavaScript
let botRunning = false;
let priceData = [];
let timeData = [];
let updateInterval;

// Initialize demo data
function initializeDemoData() {
    const now = new Date();
    const basePrice = 185420;
    
    // Generate 24 hours of price data
    for (let i = 24; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 60 * 60 * 1000);
        const variation = (Math.random() - 0.5) * 2000;
        const price = basePrice + variation;
        
        timeData.push(time.toISOString());
        priceData.push(price);
    }
    
    updateChart();
}

// Toggle bot status
function toggleBot() {
    botRunning = !botRunning;
    const statusIndicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    const toggleIcon = document.getElementById('bot-toggle-icon');
    const toggleText = document.getElementById('bot-toggle-text');
    
    if (botRunning) {
        statusIndicator.className = 'status-indicator status-running';
        statusText.textContent = 'Running';
        toggleIcon.className = 'fas fa-stop';
        toggleText.textContent = 'Stop Bot';
        
        // Start real-time updates
        startRealTimeUpdates();
        
        // Show notification
        showNotification('Bot started successfully!', 'success');
    } else {
        statusIndicator.className = 'status-indicator status-stopped';
        statusText.textContent = 'Stopped';
        toggleIcon.className = 'fas fa-play';
        toggleText.textContent = 'Start Bot';
        
        // Stop real-time updates
        stopRealTimeUpdates();
        
        // Show notification
        showNotification('Bot stopped', 'info');
    }
}

// Start real-time updates
function startRealTimeUpdates() {
    updateInterval = setInterval(() => {
        updatePriceData();
        updatePortfolioData();
        updatePerformanceData();
        addRandomTrade();
    }, 3000);
}

// Stop real-time updates
function stopRealTimeUpdates() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
}

// Update price data
function updatePriceData() {
    const currentPrice = parseFloat(document.getElementById('current-price').textContent.replace('RM ', '').replace(',', ''));
    const variation = (Math.random() - 0.5) * 500;
    const newPrice = Math.max(180000, Math.min(190000, currentPrice + variation));
    
    // Update current price
    document.getElementById('current-price').textContent = `RM ${newPrice.toLocaleString()}`;
    
    // Update bid/ask
    const spread = 40 + Math.random() * 20;
    const bid = newPrice - spread / 2;
    const ask = newPrice + spread / 2;
    
    document.getElementById('bid-price').textContent = `RM ${bid.toLocaleString()}`;
    document.getElementById('ask-price').textContent = `RM ${ask.toLocaleString()}`;
    
    // Update volume
    const volume = 140 + Math.random() * 20;
    document.getElementById('volume').textContent = `${volume.toFixed(2)} BTC`;
    
    // Add to chart data
    const now = new Date();
    timeData.push(now.toISOString());
    priceData.push(newPrice);
    
    // Keep only last 24 hours of data
    if (timeData.length > 24) {
        timeData.shift();
        priceData.shift();
    }
    
    updateChart();
}

// Update portfolio data
function updatePortfolioData() {
    const currentPrice = parseFloat(document.getElementById('current-price').textContent.replace('RM ', '').replace(',', ''));
    const btcAmount = 0.125 + (Math.random() - 0.5) * 0.01;
    const myrAmount = 5420.50 + (Math.random() - 0.5) * 100;
    
    const totalValue = (btcAmount * currentPrice) + myrAmount;
    
    document.getElementById('total-value').textContent = `RM ${totalValue.toLocaleString()}`;
}

// Update performance data
function updatePerformanceData() {
    const dailyPnl = -500 + Math.random() * 1000;
    const totalPnl = 1000 + Math.random() * 1000;
    const winRate = 60 + Math.random() * 20;
    
    const dailyPnlEl = document.getElementById('daily-pnl');
    const totalPnlEl = document.getElementById('total-pnl');
    
    dailyPnlEl.textContent = `${dailyPnl >= 0 ? '+' : ''}RM ${dailyPnl.toFixed(2)}`;
    dailyPnlEl.className = dailyPnl >= 0 ? 'positive' : 'negative';
    
    totalPnlEl.textContent = `${totalPnl >= 0 ? '+' : ''}RM ${totalPnl.toFixed(2)}`;
    totalPnlEl.className = totalPnl >= 0 ? 'positive' : 'negative';
    
    document.getElementById('win-rate').textContent = `${winRate.toFixed(1)}%`;
}

// Add random trade
function addRandomTrade() {
    if (!botRunning) return;
    
    const trades = ['BUY', 'SELL'];
    const trade = trades[Math.floor(Math.random() * trades.length)];
    const amount = (Math.random() * 0.01).toFixed(6);
    const currentPrice = parseFloat(document.getElementById('current-price').textContent.replace('RM ', '').replace(',', ''));
    const price = currentPrice + (Math.random() - 0.5) * 100;
    
    const now = new Date();
    const timestamp = now.toLocaleString();
    
    const tradeHtml = `
        <div class="trade-item simulated">
            <div>${timestamp}</div>
            <div>${trade} ${amount} BTC at RM ${price.toLocaleString()} (Simulated)</div>
        </div>
    `;
    
    const tradesContainer = document.getElementById('recent-trades');
    tradesContainer.insertAdjacentHTML('afterbegin', tradeHtml);
    
    // Keep only last 5 trades
    const tradeItems = tradesContainer.querySelectorAll('.trade-item');
    if (tradeItems.length > 5) {
        tradeItems[tradeItems.length - 1].remove();
    }
}

// Update chart
function updateChart() {
    const chartData = [{
        x: timeData,
        y: priceData,
        type: 'scatter',
        mode: 'lines',
        name: 'Price',
        line: { 
            color: '#667eea', 
            width: 2 
        },
        fill: 'tonexty',
        fillcolor: 'rgba(102, 126, 234, 0.1)'
    }];

    const layout = {
        title: {
            text: 'XBTMYR Price Movement (24h)',
            font: { size: 16, color: '#1f2937' }
        },
        xaxis: { 
            title: 'Time',
            showgrid: true,
            gridcolor: '#e5e7eb'
        },
        yaxis: { 
            title: 'Price (MYR)',
            showgrid: true,
            gridcolor: '#e5e7eb'
        },
        margin: { t: 50, r: 50, b: 50, l: 80 },
        plot_bgcolor: '#ffffff',
        paper_bgcolor: '#ffffff',
        font: { family: 'Inter, sans-serif' }
    };

    const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
        displaylogo: false
    };

    Plotly.newPlot('price-chart', chartData, layout, config);
}

// Refresh dashboard
function refreshDashboard() {
    showNotification('Dashboard refreshed', 'info');
    updatePriceData();
    updatePortfolioData();
    updatePerformanceData();
    
    // Add refresh animation
    const refreshBtn = event.target.closest('button');
    const icon = refreshBtn.querySelector('i');
    icon.style.animation = 'spin 1s linear';
    setTimeout(() => {
        icon.style.animation = '';
    }, 1000);
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Hide notification after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Add notification styles
const notificationStyles = `
    .notification {
        position: fixed;
        top: 100px;
        right: 20px;
        background: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        gap: 0.5rem;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        z-index: 1000;
        border-left: 4px solid #3b82f6;
    }
    
    .notification.show {
        transform: translateX(0);
    }
    
    .notification.success {
        border-left-color: #10b981;
    }
    
    .notification.success i {
        color: #10b981;
    }
    
    .notification.error {
        border-left-color: #ef4444;
    }
    
    .notification.error i {
        color: #ef4444;
    }
    
    .notification.info i {
        color: #3b82f6;
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
`;

// Add styles to document
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);

// Initialize demo when page loads
document.addEventListener('DOMContentLoaded', () => {
    initializeDemoData();
    
    // Show welcome notification
    setTimeout(() => {
        showNotification('Welcome to the trading bot dashboard demo!', 'info');
    }, 1000);
});

// Simulate market volatility
setInterval(() => {
    if (Math.random() < 0.1) { // 10% chance every 5 seconds
        const events = [
            'Market volatility detected',
            'Large order detected',
            'Support level tested',
            'Resistance level approached'
        ];
        const event = events[Math.floor(Math.random() * events.length)];
        showNotification(event, 'info');
    }
}, 5000);
