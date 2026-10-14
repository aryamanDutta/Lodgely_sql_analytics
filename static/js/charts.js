/**
 * Grand Luxe Hotel ERP — Chart.js Visualizations
 * Matches Image 3 visual style:
 * - Pastel bar chart for Hotel Occupancy
 * - Smooth lavender/purple line chart with gradient fill for Revenue Trend
 * - Donut chart with center total & custom legend for Bookings by Status
 */

document.addEventListener('DOMContentLoaded', function () {
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js is not loaded.');
        return;
    }

    // Design System Typography & Color Defaults
    Chart.defaults.font.family = "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
    Chart.defaults.font.size = 11;
    Chart.defaults.color = '#716D7C';

    // -------------------------------------------------------------------------
    // 1. Dashboard: Occupancy by Hotel Property (Bar Chart - Image 3 Target)
    // -------------------------------------------------------------------------
    const occEl = document.getElementById('hotelOccupancyChart');
    if (occEl) {
        try {
            const labels = JSON.parse(occEl.dataset.labels || '[]');
            const rates = JSON.parse(occEl.dataset.rates || '[]');

            // Colors matching Image 3: Orange, Lavender/Purple, Light Lavender
            const barColors = ['#FF9E66', '#B09EFA', '#C4B5FD', '#F8D5C2', '#9180E8'];

            new Chart(occEl, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        data: rates,
                        backgroundColor: barColors.slice(0, labels.length),
                        borderRadius: 8,
                        borderSkipped: false,
                        barThickness: 42
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return 'Occupancy: ' + context.parsed.y + '%';
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: {
                                maxRotation: 0,
                                autoSkip: false,
                                callback: function(val, index) {
                                    const raw = labels[index] || '';
                                    // Shorten hotel names for clean display
                                    return raw.replace('Hotel & Suites', '').replace('Resort', '').trim();
                                }
                            }
                        },
                        y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                stepSize: 20,
                                callback: function(value) { return value + '%'; }
                            },
                            grid: {
                                color: '#F0EDF8',
                                drawBorder: false
                            }
                        }
                    }
                }
            });
        } catch (e) {
            console.error('Failed to render hotel occupancy chart:', e);
        }
    }

    // -------------------------------------------------------------------------
    // 2. Dashboard: Revenue Trend (Line Chart with Gradient Fill - Image 3 Target)
    // -------------------------------------------------------------------------
    const revTrendEl = document.getElementById('revenueTrendChart');
    if (revTrendEl) {
        try {
            const labels = JSON.parse(revTrendEl.dataset.labels || '[]');
            const amounts = JSON.parse(revTrendEl.dataset.amounts || '[]');

            const ctx = revTrendEl.getContext('2d');
            const gradient = ctx.createLinearGradient(0, 0, 0, 200);
            gradient.addColorStop(0, 'rgba(191, 177, 242, 0.45)');
            gradient.addColorStop(1, 'rgba(240, 237, 248, 0.02)');

            new Chart(revTrendEl, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Collected Revenue',
                        data: amounts,
                        borderColor: '#8B5CF6',
                        borderWidth: 2.5,
                        backgroundColor: gradient,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#FFFFFF',
                        pointBorderColor: '#8B5CF6',
                        pointBorderWidth: 2.5,
                        pointRadius: 4.5,
                        pointHoverRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return 'Revenue: ₹' + Number(context.parsed.y).toLocaleString('en-IN');
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: { display: false }
                        },
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: '#F0EDF8',
                                drawBorder: false
                            },
                            ticks: {
                                callback: function(value) {
                                    if (value >= 100000) {
                                        return (value / 100000).toFixed(1) + 'L';
                                    } else if (value >= 1000) {
                                        return (value / 1000).toFixed(0) + 'K';
                                    }
                                    return value;
                                }
                            }
                        }
                    }
                }
            });
        } catch (e) {
            console.error('Failed to render revenue trend chart:', e);
        }
    }

    // -------------------------------------------------------------------------
    // 3. Dashboard: Bookings by Status (Donut Chart & Custom Legend - Image 3)
    // -------------------------------------------------------------------------
    const donutEl = document.getElementById('bookingStatusDonut');
    if (donutEl) {
        try {
            const rawLabels = JSON.parse(donutEl.dataset.labels || '[]');
            const rawCounts = JSON.parse(donutEl.dataset.counts || '[]');

            // Canonical order: Confirmed, Completed, Pending, Cancelled
            const statusConfig = {
                'Confirmed': { color: '#FF762F', order: 1 },
                'Completed': { color: '#8B5CF6', order: 2 },
                'Pending':   { color: '#C4B5FD', order: 3 },
                'Cancelled': { color: '#F87171', order: 4 }
            };

            const dataMap = {};
            rawLabels.forEach((label, i) => {
                dataMap[label] = Number(rawCounts[i]) || 0;
            });

            const labels = [];
            const counts = [];
            const colors = [];

            Object.keys(statusConfig).forEach(st => {
                labels.push(st);
                counts.push(dataMap[st] || 0);
                colors.push(statusConfig[st].color);
            });

            new Chart(donutEl, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: counts,
                        backgroundColor: colors,
                        borderWidth: 3,
                        borderColor: '#FFFFFF',
                        cutout: '72%'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    }
                }
            });

            // Populate custom legend matching Image 3
            const legendEl = document.getElementById('donutCustomLegend');
            if (legendEl) {
                legendEl.innerHTML = labels.map((st, i) => `
                    <div class="donut-legend-item">
                        <div class="donut-legend-item-left">
                            <span class="donut-legend-dot" style="background-color: ${colors[i]};"></span>
                            <span>${st}</span>
                        </div>
                        <span class="donut-legend-count">${counts[i]}</span>
                    </div>
                `).join('');
            }
        } catch (e) {
            console.error('Failed to render booking status donut:', e);
        }
    }

    // -------------------------------------------------------------------------
    // 4. Analytics Page Charts (Preserved for /analytics/)
    // -------------------------------------------------------------------------
    const analyticsRevEl = document.getElementById('monthlyRevenueChart');
    if (analyticsRevEl) {
        try {
            const labels = JSON.parse(analyticsRevEl.dataset.labels || '[]');
            const amounts = JSON.parse(analyticsRevEl.dataset.amounts || '[]');

            new Chart(analyticsRevEl, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Collected Revenue (₹)',
                        data: amounts,
                        borderColor: '#8B5CF6',
                        backgroundColor: 'rgba(191, 177, 242, 0.25)',
                        fill: true,
                        tension: 0.35,
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
            console.error('Analytics revenue chart error:', e);
        }
    }

    const analyticsHotelEl = document.getElementById('hotelBookingsChart');
    if (analyticsHotelEl) {
        try {
            const labels = JSON.parse(analyticsHotelEl.dataset.labels || '[]');
            const counts = JSON.parse(analyticsHotelEl.dataset.counts || '[]');

            new Chart(analyticsHotelEl, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Bookings Count',
                        data: counts,
                        backgroundColor: ['#FF9E66', '#B09EFA', '#C4B5FD'],
                        borderRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true, ticks: { precision: 0 } }
                    }
                }
            });
        } catch (e) {
            console.error('Analytics hotel bookings chart error:', e);
        }
    }
});
