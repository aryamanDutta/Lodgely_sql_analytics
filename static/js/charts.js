// Chart initialization helper with graceful fallback
document.addEventListener('DOMContentLoaded', function () {
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js library is not loaded. Skipping chart rendering.');
        document.querySelectorAll('.chart-fallback').forEach(function(el) {
            el.style.display = 'block';
        });
        return;
    }

    // Default chart styling
    Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    Chart.defaults.color = '#64748b';

    // 1. Dashboard Booking Status Chart (Donut / Doughnut)
    const bookingStatusEl = document.getElementById('bookingStatusChart');
    if (bookingStatusEl) {
        try {
            const labels = JSON.parse(bookingStatusEl.dataset.labels || '[]');
            const counts = JSON.parse(bookingStatusEl.dataset.counts || '[]');
            
            new Chart(bookingStatusEl, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: counts,
                        backgroundColor: [
                            '#16a34a', // Confirmed - green
                            '#d97706', // Pending - amber
                            '#2563eb', // Completed - blue
                            '#dc2626'  // Cancelled - red
                        ],
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom' }
                    }
                }
            });
        } catch (e) {
            console.error('Failed to render booking status chart', e);
        }
    }

    // 2. Dashboard Room Types Chart (Bar)
    const roomTypesEl = document.getElementById('roomTypesChart');
    if (roomTypesEl) {
        try {
            const labels = JSON.parse(roomTypesEl.dataset.labels || '[]');
            const counts = JSON.parse(roomTypesEl.dataset.counts || '[]');

            new Chart(roomTypesEl, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Rooms Count',
                        data: counts,
                        backgroundColor: '#3b82f6',
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true, ticks: { precision: 0 } }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        } catch (e) {
            console.error('Failed to render room types chart', e);
        }
    }

    // 3. Analytics Monthly Revenue Chart (Line)
    const revenueEl = document.getElementById('monthlyRevenueChart');
    if (revenueEl) {
        try {
            const labels = JSON.parse(revenueEl.dataset.labels || '[]');
            const amounts = JSON.parse(revenueEl.dataset.amounts || '[]');

            new Chart(revenueEl, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Revenue (₹)',
                        data: amounts,
                        borderColor: '#0d9488',
                        backgroundColor: 'rgba(13, 148, 136, 0.1)',
                        fill: true,
                        tension: 0.3,
                        pointRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        } catch (e) {
            console.error('Failed to render monthly revenue chart', e);
        }
    }

    // 4. Analytics Bookings By Hotel Chart (Bar)
    const hotelBookingsEl = document.getElementById('hotelBookingsChart');
    if (hotelBookingsEl) {
        try {
            const labels = JSON.parse(hotelBookingsEl.dataset.labels || '[]');
            const counts = JSON.parse(hotelBookingsEl.dataset.counts || '[]');

            new Chart(hotelBookingsEl, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Bookings Count',
                        data: counts,
                        backgroundColor: '#6366f1',
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true, ticks: { precision: 0 } }
                    },
                    plugins: { legend: { display: false } }
                }
            });
        } catch (e) {
            console.error('Failed to render hotel bookings chart', e);
        }
    }
});
