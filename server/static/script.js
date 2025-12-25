document.addEventListener('DOMContentLoaded', function() {
    // Connect to Socket.io server
    const socket = io();
    
    // Set current date
    const today = new Date();
    const options = { weekday: 'short', day: 'numeric', month: 'short' };
    document.getElementById('current-date').textContent = today.toLocaleDateString('en-US', options);
    
    // Theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = themeToggle.querySelector('i');
    
    themeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark');
        if (document.body.classList.contains('dark')) {
            themeIcon.className = 'fas fa-sun';
        } else {
            themeIcon.className = 'fas fa-moon';
        }
    });
    
    // Close alert
    const alertBox = document.getElementById('alert-box');
    const closeAlert = document.querySelector('.close-alert');
    
    closeAlert.addEventListener('click', function() {
        alertBox.classList.remove('visible');
    });
    
    // Initialize charts
    initializeCharts();
    
    // Breathing exercise
    const breathingCircle = document.getElementById('breathing-circle');
    const breathingInstruction = document.getElementById('breathing-instruction');
    const startBreathingButton = document.getElementById('start-breathing');
    let breathingInterval;
    let isBreathingActive = false;
    let breathingPhase = 'inhale';
    let breathingCounter = 0;
    
    startBreathingButton.addEventListener('click', function() {
        if (isBreathingActive) {
            clearInterval(breathingInterval);
            breathingCircle.className = 'breathing-circle';
            breathingInstruction.textContent = 'Click to start';
            startBreathingButton.textContent = 'Start';
            startBreathingButton.classList.remove('active');
            isBreathingActive = false;
        } else {
            startBreathingExercise();
            startBreathingButton.textContent = 'Stop';
            startBreathingButton.classList.add('active');
        }
    });
    
    breathingCircle.addEventListener('click', function() {
        if (!isBreathingActive) {
            startBreathingExercise();
            startBreathingButton.textContent = 'Stop';
            startBreathingButton.classList.add('active');
        }
    });
    
    function startBreathingExercise() {
        isBreathingActive = true;
        breathingPhase = 'inhale';
        breathingCounter = 0;
        updateBreathingCircle();
        
        breathingInterval = setInterval(function() {
            breathingCounter++;
            
            if (breathingPhase === 'inhale' && breathingCounter >= 4) {
                breathingPhase = 'hold';
                breathingCounter = 0;
                updateBreathingCircle();
            } else if (breathingPhase === 'hold' && breathingCounter >= 7) {
                breathingPhase = 'exhale';
                breathingCounter = 0;
                updateBreathingCircle();
            } else if (breathingPhase === 'exhale' && breathingCounter >= 8) {
                breathingPhase = 'inhale';
                breathingCounter = 0;
                updateBreathingCircle();
            }
        }, 1000);
    }
    
    function updateBreathingCircle() {
        breathingCircle.className = 'breathing-circle ' + breathingPhase;
        
        if (breathingPhase === 'inhale') {
            breathingInstruction.textContent = 'Inhale slowly through your nose...';
        } else if (breathingPhase === 'hold') {
            breathingInstruction.textContent = 'Hold your breath...';
        } else {
            breathingInstruction.textContent = 'Exhale slowly through your mouth...';
        }
    }
    
    // Socket.io event listeners
    socket.on('connect', function() {
        console.log('Connected to server');
        document.getElementById('last-updated').textContent = 'Connected';
    });
    
    // Listen for sensor data updates
    socket.on('sensor_data', function(data) {
        updateDashboard(data);
        updateCharts(data);
    });
    
    // Listen for fall alerts
    socket.on('fall_alert', function(alertData) {
        document.getElementById('alert-message').textContent = alertData.message;
        alertBox.classList.add('visible');
        
        // Hide alert after 5 seconds
        setTimeout(function() {
            alertBox.classList.remove('visible');
        }, 5000);
    });
    
    function updateDashboard(data) {
        // Update heart rate
        document.getElementById('heart-rate-value').textContent = data.heart_rate;
        
        // Update SpO2
        document.getElementById('spo2-value').textContent = data.spo2;
        
        // Update temperature
        document.getElementById('temperature-value').textContent = data.temperature;
        
        // Update movement status
        const movementIcon = document.getElementById('movement-icon');
        const movementStatus = document.getElementById('movement-status');
        
        if (data.fall_detected) {
            movementIcon.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
            movementIcon.className = 'status-icon danger';
            movementStatus.textContent = 'Fall Detected!';
        } else {
            movementIcon.innerHTML = '<i class="fas fa-check-circle"></i>';
            movementIcon.className = 'status-icon';
            movementStatus.textContent = 'Normal';
        }
        
        // Update predicted disease
        const predictedDisease = document.getElementById('predicted-disease');
        const predictionIcon = document.querySelector('.prediction-result i');
        
        predictedDisease.textContent = data.prediction;
        
        if (data.prediction !== 'No Disease Detected') {
            predictionIcon.className = 'fas fa-exclamation-circle warning';
        } else {
            predictionIcon.className = 'fas fa-check-circle';
        }
        
        // Update health status indicators
        updateHealthStatus(data.heart_rate, data.spo2, parseFloat(data.temperature));
        
        // Update last updated time
        const now = new Date();
        document.getElementById('last-updated').textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    // Update health status indicators based on values
    function updateHealthStatus(heartRate, spo2, temperature) {
        // Heart rate status
        const heartRateStatus = document.querySelector('.heart-rate .status');
        if (heartRate > 100) {
            heartRateStatus.className = 'status danger';
            heartRateStatus.textContent = 'Elevated';
        } else if (heartRate < 60) {
            heartRateStatus.className = 'status warning';
            heartRateStatus.textContent = 'Low';
        } else {
            heartRateStatus.className = 'status normal';
            heartRateStatus.textContent = 'Normal';
        }
        
        // SpO2 status
        const spo2Status = document.querySelector('.spo2 .status');
        if (spo2 < 95) {
            spo2Status.className = 'status danger';
            spo2Status.textContent = 'Low';
        } else {
            spo2Status.className = 'status normal';
            spo2Status.textContent = 'Normal';
        }
        
        // Temperature status
        const tempStatus = document.querySelector('.temperature .status');
        if (temperature > 37.5) {
            tempStatus.className = 'status danger';
            tempStatus.textContent = 'Fever';
        } else if (temperature < 36) {
            tempStatus.className = 'status warning';
            tempStatus.textContent = 'Low';
        } else {
            tempStatus.className = 'status normal';
            tempStatus.textContent = 'Normal';
        }
    }
});

function initializeCharts() {
    // Chart configuration
    const chartConfig = {
        type: 'line',
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: true
                }
            },
            scales: {
                x: {
                    display: false
                },
                y: {
                    display: false
                }
            },
            elements: {
                line: {
                    tension: 0.4
                },
                point: {
                    radius: 0
                }
            }
        }
    };
    
    // Generate initial data for charts
    const generateChartData = (min, max, count = 12) => {
        return Array.from({ length: count }, () => 
            Math.floor(Math.random() * (max - min + 1)) + min
        );
    };
    
    // Heart Rate Chart
    const heartRateCtx = document.getElementById('heartRateChart').getContext('2d');
    const heartRateData = {
        labels: Array.from({ length: 12 }, (_, i) => i),
        datasets: [{
            data: generateChartData(65, 100),
            borderColor: '#3a86ff',
            backgroundColor: 'rgba(58, 134, 255, 0.1)',
            fill: true
        }]
    };
    const heartRateChart = new Chart(heartRateCtx, {
        ...chartConfig,
        data: heartRateData
    });
    
    // SpO2 Chart
    const spo2Ctx = document.getElementById('spo2Chart').getContext('2d');
    const spo2Data = {
        labels: Array.from({ length: 12 }, (_, i) => i),
        datasets: [{
            data: generateChartData(94, 100),
            borderColor: '#4ade80',
            backgroundColor: 'rgba(74, 222, 128, 0.1)',
            fill: true
        }]
    };
    const spo2Chart = new Chart(spo2Ctx, {
        ...chartConfig,
        data: spo2Data
    });
    
    // Temperature Chart
    const temperatureCtx = document.getElementById('temperatureChart').getContext('2d');
    const temperatureData = {
        labels: Array.from({ length: 12 }, (_, i) => i),
        datasets: [{
            data: generateChartData(36, 37.5, 12).map(val => parseFloat(val.toFixed(1))),
            borderColor: '#ffca3a',
            backgroundColor: 'rgba(255, 202, 58, 0.1)',
            fill: true
        }]
    };
    const temperatureChart = new Chart(temperatureCtx, {
        ...chartConfig,
        data: temperatureData
    });
    
    // Store charts in window object for later updates
    window.dashboardCharts = {
        heartRateChart,
        spo2Chart,
        temperatureChart
    };
}

function updateCharts(data) {
    if (!window.dashboardCharts) return;
    
    // Update heart rate chart
    if (window.dashboardCharts.heartRateChart) {
        window.dashboardCharts.heartRateChart.data.datasets[0].data.push(data.heart_rate);
        window.dashboardCharts.heartRateChart.data.datasets[0].data.shift();
        window.dashboardCharts.heartRateChart.update();
    }
    
    // Update SpO2 chart
    if (window.dashboardCharts.spo2Chart) {
        window.dashboardCharts.spo2Chart.data.datasets[0].data.push(data.spo2);
        window.dashboardCharts.spo2Chart.data.datasets[0].data.shift();
        window.dashboardCharts.spo2Chart.update();
    }
    
    // Update temperature chart
    if (window.dashboardCharts.temperatureChart) {
        window.dashboardCharts.temperatureChart.data.datasets[0].data.push(parseFloat(data.temperature));
        window.dashboardCharts.temperatureChart.data.datasets[0].data.shift();
        window.dashboardCharts.temperatureChart.update();
    }
}