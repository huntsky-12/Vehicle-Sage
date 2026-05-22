// // Vehicle Telemetry Dashboard Application
// class VehicleDashboard {
//     constructor() {
//         this.vehicles = [];
//         this.map = null;
//         this.markers = {};
//         this.charts = {};
//         this.currentPage = 'dashboard';
//         this.updateInterval = null;
//         this.baseURL = 'http://localhost:8000';
//         this.connectionStatus = 'connecting';
        
//         this.init();
//     }

//     init() {
//         this.setupEventListeners();
//         this.loadInitialData();
//         this.startRealTimeUpdates();
//         this.updateConnectionStatus('connecting');
//     }

//     setupEventListeners() {
//         // Navigation
//         document.querySelectorAll('.nav-link').forEach(link => {
//             link.addEventListener('click', (e) => {
//                 e.preventDefault();
//                 const page = e.target.dataset.page;
//                 this.navigateToPage(page);
//             });
//         });

//         // Hamburger menu
//         const hamburger = document.getElementById('hamburger');
//         if (hamburger) {
//             hamburger.addEventListener('click', () => {
//                 document.getElementById('nav-menu').classList.toggle('active');
//             });
//         }

//         // Vehicle form buttons - handle both add buttons
//         const addVehicleBtn = document.getElementById('add-vehicle-btn');
//         const addVehicleBtn2 = document.getElementById('add-vehicle-btn-2');
//         if (addVehicleBtn) {
//             addVehicleBtn.addEventListener('click', () => this.showVehicleModal());
//         }
//         if (addVehicleBtn2) {
//             addVehicleBtn2.addEventListener('click', () => this.showVehicleModal());
//         }

//         const saveBtn = document.getElementById('save-btn');
//         if (saveBtn) {
//             saveBtn.addEventListener('click', () => this.saveVehicle());
//         }

//         const cancelBtn = document.getElementById('cancel-btn');
//         if (cancelBtn) {
//             cancelBtn.addEventListener('click', () => this.hideVehicleModal());
//         }

//         // Modal close buttons
//         document.querySelectorAll('.modal-close, .modal-overlay').forEach(el => {
//             el.addEventListener('click', (e) => {
//                 if (e.target === el) {
//                     this.hideAllModals();
//                 }
//             });
//         });

//         // Analytics controls
//         const updateChartsBtn = document.getElementById('update-charts');
//         if (updateChartsBtn) {
//             updateChartsBtn.addEventListener('click', () => {
//                 this.updateAnalyticsCharts();
//             });
//         }

//         // Set default dates
//         this.setDefaultDates();
//     }

//     setDefaultDates() {
//         const today = new Date();
//         const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
//         const startDate = document.getElementById('start-date');
//         const endDate = document.getElementById('end-date');
//         if (startDate) startDate.value = weekAgo.toISOString().split('T')[0];
//         if (endDate) endDate.value = today.toISOString().split('T')[0];
//     }

//     async loadInitialData() {
//         try {
//             this.showLoading(true);
//             await this.fetchVehicles();
//             this.updateConnectionStatus('connected');
//         } catch (error) {
//             console.error('Error loading initial data:', error);
//             this.updateConnectionStatus('error');
//             this.showNotification('Failed to load vehicle data from server, using sample data', 'warning');
//         } finally {
//             this.showLoading(false);
//         }
//     }

//     async fetchVehicles() {
//         try {
//             // Try InfluxDB endpoint first
//             console.log('Fetching from InfluxDB endpoint...');
//             const response = await fetch(`${this.baseURL}/telemetry/influx`, {
//                 method: 'GET',
//                 headers: {
//                     'Content-Type': 'application/json',
//                 },
//                 // Add timeout
//                 signal: AbortSignal.timeout(10000)
//             });
            
//             if (!response.ok) {
//                 throw new Error(`HTTP error! status: ${response.status}`);
//             }
            
//             const data = await response.json();
//             console.log('Received data from InfluxDB:', data);
            
//             this.vehicles = Array.isArray(data) ? data : [];
            
//             // If no data from InfluxDB, try vehicles endpoint
//             if (this.vehicles.length === 0) {
//                 console.log('No data from InfluxDB, trying vehicles endpoint...');
//                 await this.fetchFromVehiclesEndpoint();
//             }
            
//         } catch (error) {
//             console.error('Error fetching from InfluxDB:', error);
            
//             // Try vehicles endpoint as fallback
//             try {
//                 await this.fetchFromVehiclesEndpoint();
//             } catch (fallbackError) {
//                 console.error('Fallback also failed:', fallbackError);
//                 // Use sample data as final fallback
//                 this.vehicles = this.getSampleData();
//                 this.connectionStatus = 'error';
//             }
//         }
        
//         this.updateDashboard();
//         this.updateVehiclesTable();
//         this.updateVehicleSelector();
//         if (this.map) {
//             this.updateMap();
//         }
//     }

//     async fetchFromVehiclesEndpoint() {
//         const response = await fetch(`${this.baseURL}/vehicles`, {
//             method: 'GET',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//             signal: AbortSignal.timeout(10000)
//         });
        
//         if (!response.ok) {
//             throw new Error(`HTTP error! status: ${response.status}`);
//         }
        
//         const data = await response.json();
//         console.log('Received data from vehicles endpoint:', data);
//         this.vehicles = Array.isArray(data) ? data : [];
        
//         if (this.vehicles.length === 0) {
//             this.vehicles = this.getSampleData();
//         }
//     }

//     getSampleData() {
//         // Sample data based on the provided application data
//         return [
//             {
//                 vehicle_id: "veh_0",
//                 current_location: { latitude: 37.7749, longitude: -122.4194 },
//                 current_speed: 65.5,
//                 fuel_level: 45.2,
//                 last_update: "2025-08-03T14:30:00Z",
//                 status: "active"
//             },
//             {
//                 vehicle_id: "veh_1", 
//                 current_location: { latitude: 37.7849, longitude: -122.4094 },
//                 current_speed: 0,
//                 fuel_level: 78.5,
//                 last_update: "2025-08-03T14:25:00Z",
//                 status: "idle"
//             },
//             {
//                 vehicle_id: "veh_2",
//                 current_location: { latitude: 37.7649, longitude: -122.4294 },
//                 current_speed: 45.8,
//                 fuel_level: 12.3,
//                 last_update: "2025-08-03T14:28:00Z", 
//                 status: "active"
//             },
//             {
//                 vehicle_id: "veh_3",
//                 current_location: { latitude: 37.7549, longitude: -122.4394 },
//                 current_speed: 0,
//                 fuel_level: 0,
//                 last_update: "2025-08-03T14:00:00Z",
//                 status: "offline"
//             }
//         ];
//     }

//     startRealTimeUpdates() {
//         // Update every 5 seconds as requested
//         this.updateInterval = setInterval(() => {
//             this.fetchVehicles();
//         }, 5000);
//     }

//     updateConnectionStatus(status) {
//         const indicator = document.getElementById('status-indicator');
//         const statusText = document.getElementById('status-text');
//         const lastUpdate = document.getElementById('last-update');

//         if (!indicator || !statusText || !lastUpdate) return;

//         this.connectionStatus = status;
//         indicator.className = 'status-indicator';
        
//         switch (status) {
//             case 'connected':
//                 indicator.classList.add('connected');
//                 statusText.textContent = 'Connected to InfluxDB';
//                 lastUpdate.textContent = `Last update: ${new Date().toLocaleTimeString()}`;
//                 break;
//             case 'connecting':
//                 statusText.textContent = 'Connecting to server...';
//                 lastUpdate.textContent = '';
//                 break;
//             case 'error':
//                 statusText.textContent = 'Connection Error - Using Sample Data';
//                 lastUpdate.textContent = `Sample data loaded at ${new Date().toLocaleTimeString()}`;
//                 break;
//         }
//     }

//     navigateToPage(pageName) {
//         console.log('Navigating to page:', pageName);
        
//         // Update navigation
//         document.querySelectorAll('.nav-link').forEach(link => {
//             link.classList.remove('active');
//         });
//         const activeLink = document.querySelector(`[data-page="${pageName}"]`);
//         if (activeLink) {
//             activeLink.classList.add('active');
//         }

//         // Show page
//         document.querySelectorAll('.page').forEach(page => {
//             page.classList.remove('active');
//         });
//         const targetPage = document.getElementById(`${pageName}-page`);
//         if (targetPage) {
//             targetPage.classList.add('active');
//         }

//         this.currentPage = pageName;

//         // Initialize page-specific content
//         if (pageName === 'map') {
//             setTimeout(() => this.initializeMap(), 100);
//         } else if (pageName === 'analytics') {
//             setTimeout(() => this.initializeCharts(), 100);
//         }

//         // Close mobile menu
//         const navMenu = document.getElementById('nav-menu');
//         if (navMenu) {
//             navMenu.classList.remove('active');
//         }
//     }

//     updateDashboard() {
//         // Update summary stats with zero-state handling
//         const totalVehicles = this.vehicles.length || 0;
//         const activeVehicles = this.vehicles.filter(v => v.status === 'active').length || 0;
//         const idleVehicles = this.vehicles.filter(v => v.status === 'idle').length || 0;
//         const offlineVehicles = this.vehicles.filter(v => v.status === 'offline').length || 0;

//         this.animateCounter('total-vehicles', totalVehicles);
//         this.animateCounter('active-vehicles', activeVehicles);
//         this.animateCounter('idle-vehicles', idleVehicles);
//         this.animateCounter('offline-vehicles', offlineVehicles);

//         // Update vehicle cards with zero-state handling
//         this.updateVehicleCards();
        
//         // Update alerts
//         this.updateAlerts();
//     }

//     updateVehicleCards() {
//         const vehicleCardsContainer = document.getElementById('vehicle-cards');
//         const emptyState = document.getElementById('empty-vehicles');

//         if (!vehicleCardsContainer) return;

//         // Always clear the container first
//         vehicleCardsContainer.innerHTML = '';

//         if (this.vehicles.length === 0) {
//             // Show empty state but maintain structure
//             const emptyStateElement = document.createElement('div');
//             emptyStateElement.className = 'empty-state';
//             emptyStateElement.innerHTML = '<p>No vehicles registered</p>';
//             vehicleCardsContainer.appendChild(emptyStateElement);
//         } else {
//             // Create vehicle cards
//             this.vehicles.forEach(vehicle => {
//                 const card = this.createVehicleCard(vehicle);
//                 vehicleCardsContainer.appendChild(card);
//             });
//         }
//     }

//     animateCounter(elementId, newValue) {
//         const element = document.getElementById(elementId);
//         if (!element) return;
        
//         const currentValue = parseInt(element.textContent) || 0;
        
//         // Always show the value, even if it's 0
//         element.textContent = newValue;
        
//         if (currentValue !== newValue) {
//             element.classList.add('animate');
//             setTimeout(() => {
//                 element.classList.remove('animate');
//             }, 300);
//         }
//     }
// createVehicleCard(vehicle) {
//     const card = document.createElement('div');
//     card.className = 'vehicle-card';
//     card.addEventListener('click', () => this.showVehicleDetails(vehicle));

//     const lastUpdate = new Date(vehicle.last_update);
//     const formattedTime = isNaN(lastUpdate) ? "Invalid time" : lastUpdate.toLocaleString();

//     // Safe value formatting with fallback
//     const speed = (typeof vehicle.current_speed === "number") 
//         ? vehicle.current_speed.toFixed(1) 
//         : "N/A";
//     const fuel = (typeof vehicle.fuel_level === "number") 
//         ? vehicle.fuel_level.toFixed(1) 
//         : "N/A";

//     card.innerHTML = `
//         <div class="vehicle-card-header">
//             <div class="vehicle-id">${vehicle.vehicle_id}</div>
//             <div class="vehicle-status ${vehicle.status}">${vehicle.status}</div>
//         </div>
//         <div class="vehicle-metrics">
//             <div class="metric">
//                 <div class="metric-value">${speed}</div>
//                 <div class="metric-label">Speed (km/h)</div>
//             </div>
//             <div class="metric">
//                 <div class="metric-value">${fuel}</div>
//                 <div class="metric-label">Fuel (L)</div>
//             </div>
//         </div>
//         <div class="vehicle-timestamp">Last update: ${formattedTime}</div>
//     `;

//     return card;
// }

//     updateAlerts() {
//         const alertsList = document.getElementById('alerts-list');
//         if (!alertsList) return;
        
//         const alerts = [];

//         // Generate alerts based on vehicle data
//         this.vehicles.forEach(vehicle => {
//             if (vehicle.fuel_level < 20 && vehicle.fuel_level > 0) {
//                 alerts.push({
//                     type: 'warning',
//                     text: `${vehicle.vehicle_id} has low fuel (${vehicle.fuel_level.toFixed(1)}L)`,
//                     time: new Date(vehicle.last_update)
//                 });
//             }
            
//             if (vehicle.fuel_level === 0) {
//                 alerts.push({
//                     type: 'error',
//                     text: `${vehicle.vehicle_id} is out of fuel`,
//                     time: new Date(vehicle.last_update)
//                 });
//             }
            
//             if (vehicle.current_speed > 80) {
//                 alerts.push({
//                     type: 'error',
//                     text: `${vehicle.vehicle_id} is speeding (${vehicle.current_speed.toFixed(1)} km/h)`,
//                     time: new Date(vehicle.last_update)
//                 });
//             }
            
//             if (vehicle.status === 'offline') {
//                 alerts.push({
//                     type: 'error',
//                     text: `${vehicle.vehicle_id} is offline`,
//                     time: new Date(vehicle.last_update)
//                 });
//             }
//         });

//         // Sort alerts by time (newest first)
//         alerts.sort((a, b) => b.time - a.time);
        
//         // Always maintain the alerts structure
//         alertsList.innerHTML = '';
        
//         if (alerts.length === 0) {
//             const emptyAlert = document.createElement('div');
//             emptyAlert.className = 'empty-state';
//             emptyAlert.innerHTML = '<p>No alerts</p>';
//             alertsList.appendChild(emptyAlert);
//         } else {
//             alerts.slice(0, 5).forEach(alert => {
//                 const alertElement = document.createElement('div');
//                 alertElement.className = `alert-item ${alert.type}`;
//                 alertElement.innerHTML = `
//                     <div class="alert-text">${alert.text}</div>
//                     <div class="alert-time">${alert.time.toLocaleTimeString()}</div>
//                 `;
//                 alertsList.appendChild(alertElement);
//             });
//         }
//     }

//     updateVehiclesTable() {
//         const tbody = document.getElementById('vehicles-tbody');
//         if (!tbody) return;
        
//         tbody.innerHTML = '';
        
//         if (this.vehicles.length === 0) {
//             tbody.innerHTML = '<tr class="empty-row"><td colspan="6">No vehicles registered</td></tr>';
//             return;
//         }

//         this.vehicles.forEach(vehicle => {
//             const row = document.createElement('tr');
//             const lastUpdate = new Date(vehicle.last_update);
            
//             row.innerHTML = `
//                 <td>${vehicle.vehicle_id}</td>
//                 <td><span class="vehicle-status ${vehicle.status}">${vehicle.status}</span></td>
//                 <td>${vehicle.current_speed.toFixed(1)}</td>
//                 <td>${vehicle.fuel_level.toFixed(1)}</td>
//                 <td>${lastUpdate.toLocaleString()}</td>
//                 <td>
//                     <div class="action-buttons">
//                         <button class="btn-icon" onclick="window.dashboard.showVehicleDetails('${vehicle.vehicle_id}')" title="View Details">👁️</button>
//                         <button class="btn-icon" onclick="window.dashboard.editVehicle('${vehicle.vehicle_id}')" title="Edit">✏️</button>
//                         <button class="btn-icon" onclick="window.dashboard.deleteVehicle('${vehicle.vehicle_id}')" title="Delete">🗑️</button>
//                     </div>
//                 </td>
//             `;
//             tbody.appendChild(row);
//         });
//     }

//     initializeMap() {
//         if (this.map) {
//             this.map.remove();
//         }

//         const mapContainer = document.getElementById('map');
//         if (!mapContainer) return;

//         try {
//             // Initialize map centered on San Francisco
//             this.map = L.map('map').setView([37.7749, -122.4194], 12);

//             // Add tile layer
//             L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
//                 attribution: '© OpenStreetMap contributors'
//             }).addTo(this.map);

//             this.updateMap();
//         } catch (error) {
//             console.error('Error initializing map:', error);
//             this.showNotification('Failed to initialize map', 'error');
//         }
//     }

//     updateMap() {
//         if (!this.map) return;

//         // Clear existing markers
//         Object.values(this.markers).forEach(marker => {
//             this.map.removeLayer(marker);
//         });
//         this.markers = {};

//         // Add markers for each vehicle
//         this.vehicles.forEach(vehicle => {
//             const lat = vehicle.current_location.latitude;
//             const lng = vehicle.current_location.longitude;
            
//             let markerColor = 'red';
//             if (vehicle.status === 'active') markerColor = 'green';
//             else if (vehicle.status === 'idle') markerColor = 'orange';

//             const marker = L.circleMarker([lat, lng], {
//                 color: markerColor,
//                 fillColor: markerColor,
//                 fillOpacity: 0.7,
//                 radius: 8
//             }).addTo(this.map);

//             // Add popup with vehicle details
//             const popupContent = `
//                 <div>
//                     <h4>${vehicle.vehicle_id}</h4>
//                     <p><strong>Status:</strong> ${vehicle.status}</p>
//                     <p><strong>Speed:</strong> ${vehicle.current_speed.toFixed(1)} km/h</p>
//                     <p><strong>Fuel:</strong> ${vehicle.fuel_level.toFixed(1)} L</p>
//                     <p><strong>Last Update:</strong> ${new Date(vehicle.last_update).toLocaleString()}</p>
//                 </div>
//             `;
//             marker.bindPopup(popupContent);

//             this.markers[vehicle.vehicle_id] = marker;
//         });

//         // Fit map to show all markers if vehicles exist
//         if (this.vehicles.length > 0) {
//             const group = new L.featureGroup(Object.values(this.markers));
//             this.map.fitBounds(group.getBounds().pad(0.1));
//         }
//     }

//     updateVehicleSelector() {
//         const selector = document.getElementById('vehicle-selector');
//         if (!selector) return;
        
//         selector.innerHTML = '<option value="">All Vehicles</option>';
        
//         this.vehicles.forEach(vehicle => {
//             const option = document.createElement('option');
//             option.value = vehicle.vehicle_id;
//             option.textContent = vehicle.vehicle_id;
//             selector.appendChild(option);
//         });
//     }

//     initializeCharts() {
//         this.createSpeedChart();
//         this.createFuelChart();
//     }

//     createSpeedChart() {
//         const ctx = document.getElementById('speed-chart');
//         if (!ctx) return;

//         if (this.charts.speed) {
//             this.charts.speed.destroy();
//         }

//         // Generate sample time series data
//         const labels = [];
//         const data = [];
//         const now = new Date();
        
//         for (let i = 23; i >= 0; i--) {
//             const time = new Date(now.getTime() - i * 60 * 60 * 1000);
//             labels.push(time.toLocaleTimeString());
            
//             // Generate sample data based on current vehicles
//             if (this.vehicles.length > 0) {
//                 const avgSpeed = this.vehicles.reduce((sum, v) => sum + v.current_speed, 0) / this.vehicles.length;
//                 data.push(Math.max(0, avgSpeed + (Math.random() - 0.5) * 20));
//             } else {
//                 data.push(0);
//             }
//         }

//         this.charts.speed = new Chart(ctx, {
//             type: 'line',
//             data: {
//                 labels: labels,
//                 datasets: [{
//                     label: 'Average Speed (km/h)',
//                     data: data,
//                     borderColor: '#1FB8CD',
//                     backgroundColor: 'rgba(31, 184, 205, 0.1)',
//                     tension: 0.4,
//                     fill: true
//                 }]
//             },
//             options: {
//                 responsive: true,
//                 maintainAspectRatio: false,
//                 plugins: {
//                     legend: {
//                         display: true
//                     }
//                 },
//                 scales: {
//                     y: {
//                         beginAtZero: true,
//                         title: {
//                             display: true,
//                             text: 'Speed (km/h)'
//                         }
//                     }
//                 }
//             }
//         });
//     }

//     createFuelChart() {
//         const ctx = document.getElementById('fuel-chart');
//         if (!ctx) return;

//         if (this.charts.fuel) {
//             this.charts.fuel.destroy();
//         }

//         // Handle empty state for fuel chart
//         if (this.vehicles.length === 0) {
//             this.charts.fuel = new Chart(ctx, {
//                 type: 'bar',
//                 data: {
//                     labels: ['No Data'],
//                     datasets: [{
//                         label: 'Fuel Level (L)',
//                         data: [0],
//                         backgroundColor: '#1FB8CD',
//                         borderColor: '#1FB8CD',
//                         borderWidth: 1
//                     }]
//                 },
//                 options: {
//                     responsive: true,
//                     maintainAspectRatio: false,
//                     plugins: {
//                         legend: {
//                             display: true
//                         }
//                     },
//                     scales: {
//                         y: {
//                             beginAtZero: true,
//                             title: {
//                                 display: true,
//                                 text: 'Fuel Level (L)'
//                             }
//                         }
//                     }
//                 }
//             });
//             return;
//         }

//         // Create fuel level data for each vehicle
//         const colors = ['#1FB8CD', '#FFC185', '#B4413C', '#ECEBD5', '#5D878F', '#DB4545', '#D2BA4C', '#964325', '#944454', '#13343B'];
//         const datasets = this.vehicles.map((vehicle, index) => {
//             return {
//                 label: vehicle.vehicle_id,
//                 data: [vehicle.fuel_level],
//                 backgroundColor: colors[index % colors.length],
//                 borderColor: colors[index % colors.length],
//                 borderWidth: 1
//             };
//         });

//         this.charts.fuel = new Chart(ctx, {
//             type: 'bar',
//             data: {
//                 labels: ['Current Fuel Level'],
//                 datasets: datasets
//             },
//             options: {
//                 responsive: true,
//                 maintainAspectRatio: false,
//                 plugins: {
//                     legend: {
//                         display: true
//                     }
//                 },
//                 scales: {
//                     y: {
//                         beginAtZero: true,
//                         title: {
//                             display: true,
//                             text: 'Fuel Level (L)'
//                         }
//                     }
//                 }
//             }
//         });
//     }

//     updateAnalyticsCharts() {
//         const startDate = document.getElementById('start-date');
//         const endDate = document.getElementById('end-date');
//         const selectedVehicle = document.getElementById('vehicle-selector');

//         const startValue = startDate ? startDate.value : '';
//         const endValue = endDate ? endDate.value : '';
//         const vehicleValue = selectedVehicle ? selectedVehicle.value : '';

//         // In a real application, you would fetch filtered data here
//         this.createSpeedChart();
//         this.createFuelChart();

//         const message = vehicleValue 
//             ? `Charts updated for ${vehicleValue} (${startValue} to ${endValue})`
//             : `Charts updated for all vehicles (${startValue} to ${endValue})`;
            
//         this.showNotification(message, 'success');
//     }

//     showVehicleModal(vehicle = null) {
//         const modal = document.getElementById('vehicle-modal');
//         const title = document.getElementById('modal-title');
//         const form = document.getElementById('vehicle-form');

//         if (!modal || !title || !form) return;

//         if (vehicle) {
//             title.textContent = 'Edit Vehicle';
//             document.getElementById('vehicle-id').value = vehicle.vehicle_id;
//             document.getElementById('vehicle-lat').value = vehicle.current_location.latitude;
//             document.getElementById('vehicle-lng').value = vehicle.current_location.longitude;
//             document.getElementById('vehicle-speed').value = vehicle.current_speed;
//             document.getElementById('vehicle-fuel').value = vehicle.fuel_level;
//         } else {
//             title.textContent = 'Add Vehicle';
//             form.reset();
//         }

//         modal.classList.remove('hidden');
//     }

//     hideVehicleModal() {
//         const modal = document.getElementById('vehicle-modal');
//         if (modal) {
//             modal.classList.add('hidden');
//         }
//     }

//     async saveVehicle() {
//         const form = document.getElementById('vehicle-form');
//         if (!form || !form.checkValidity()) {
//             if (form) form.reportValidity();
//             return;
//         }

//         const vehicleData = {
//             vehicle_id: document.getElementById('vehicle-id').value,
//             current_location: {
//                 latitude: parseFloat(document.getElementById('vehicle-lat').value),
//                 longitude: parseFloat(document.getElementById('vehicle-lng').value)
//             },
//             current_speed: parseFloat(document.getElementById('vehicle-speed').value),
//             fuel_level: parseFloat(document.getElementById('vehicle-fuel').value),
//             last_update: new Date().toISOString(),
//             status: 'active'
//         };

//         try {
//             this.showLoading(true);
            
//             // Try to save to backend
//             const response = await fetch(`${this.baseURL}/register_vehicle`, {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json'
//                 },
//                 body: JSON.stringify(vehicleData),
//                 signal: AbortSignal.timeout(10000)
//             });

//             if (response.ok) {
//                 this.showNotification('Vehicle saved successfully', 'success');
//             } else {
//                 throw new Error('Failed to save vehicle to server');
//             }
            
//         } catch (error) {
//             console.error('Error saving vehicle:', error);
//             // Add to local data as fallback
//             const existingIndex = this.vehicles.findIndex(v => v.vehicle_id === vehicleData.vehicle_id);
//             if (existingIndex >= 0) {
//                 this.vehicles[existingIndex] = vehicleData;
//             } else {
//                 this.vehicles.push(vehicleData);
//             }
//             this.showNotification('Vehicle saved locally (server unavailable)', 'warning');
//         } finally {
//             this.showLoading(false);
//             this.hideVehicleModal();
//             this.updateDashboard();
//             this.updateVehiclesTable();
//             if (this.map) this.updateMap();
//             this.updateVehicleSelector();
//         }
//     }

//     showVehicleDetails(vehicleId) {
//         const vehicle = typeof vehicleId === 'string' 
//             ? this.vehicles.find(v => v.vehicle_id === vehicleId)
//             : vehicleId;
            
//         if (!vehicle) return;

//         const modal = document.getElementById('details-modal');
//         const detailsContainer = document.getElementById('vehicle-details');

//         if (!modal || !detailsContainer) return;

//         detailsContainer.innerHTML = `
//             <div class="vehicle-detail-grid">
//                 <div class="detail-row">
//                     <strong>Vehicle ID:</strong> <span>${vehicle.vehicle_id}</span>
//                 </div>
//                 <div class="detail-row">
//                     <strong>Status:</strong> <span class="vehicle-status ${vehicle.status}">${vehicle.status}</span>
//                 </div>
//                 <div class="detail-row">
//                     <strong>Current Speed:</strong> <span>${vehicle.current_speed.toFixed(1)} km/h</span>
//                 </div>
//                 <div class="detail-row">
//                     <strong>Fuel Level:</strong> <span>${vehicle.fuel_level.toFixed(1)} L</span>
//                 </div>
//                 <div class="detail-row">
//                     <strong>Location:</strong> <span>${vehicle.current_location.latitude.toFixed(4)}, ${vehicle.current_location.longitude.toFixed(4)}</span>
//                 </div>
//                 <div class="detail-row">
//                     <strong>Last Update:</strong> <span>${new Date(vehicle.last_update).toLocaleString()}</span>
//                 </div>
//             </div>
//         `;

//         modal.classList.remove('hidden');
//     }

//     editVehicle(vehicleId) {
//         const vehicle = this.vehicles.find(v => v.vehicle_id === vehicleId);
//         if (vehicle) {
//             this.showVehicleModal(vehicle);
//         }
//     }

//     async deleteVehicle(vehicleId) {
//         if (!confirm(`Are you sure you want to delete vehicle ${vehicleId}?`)) {
//             return;
//         }

//         try {
//             // Try to delete from server
//             const response = await fetch(`${this.baseURL}/vehicles/${vehicleId}`, {
//                 method: 'DELETE',
//                 signal: AbortSignal.timeout(10000)
//             });

//             if (!response.ok && response.status !== 404) {
//                 throw new Error('Failed to delete from server');
//             }
            
//         } catch (error) {
//             console.error('Error deleting vehicle from server:', error);
//             this.showNotification('Server deletion failed, removing locally', 'warning');
//         }

//         // Remove locally regardless of server response
//         this.vehicles = this.vehicles.filter(v => v.vehicle_id !== vehicleId);
//         this.updateDashboard();
//         this.updateVehiclesTable();
//         if (this.map) this.updateMap();
//         this.updateVehicleSelector();
//         this.showNotification('Vehicle deleted successfully', 'success');
//     }

//     hideAllModals() {
//         document.querySelectorAll('.modal').forEach(modal => {
//             modal.classList.add('hidden');
//         });
//     }

//     showLoading(show) {
//         const overlay = document.getElementById('loading-overlay');
//         if (overlay) {
//             if (show) {
//                 overlay.classList.remove('hidden');
//             } else {
//                 overlay.classList.add('hidden');
//             }
//         }
//     }

//     showNotification(message, type = 'info') {
//         const container = document.getElementById('notifications');
//         if (!container) return;
        
//         const notification = document.createElement('div');
//         notification.className = `notification ${type}`;
//         notification.textContent = message;

//         container.appendChild(notification);

//         // Auto remove after 5 seconds
//         setTimeout(() => {
//             if (notification.parentNode) {
//                 notification.parentNode.removeChild(notification);
//             }
//         }, 5000);
//     }

//     // Cleanup method
//     destroy() {
//         if (this.updateInterval) {
//             clearInterval(this.updateInterval);
//         }
//         if (this.map) {
//             this.map.remove();
//         }
//         Object.values(this.charts).forEach(chart => {
//             if (chart) chart.destroy();
//         });
//     }
// }

// // Initialize the dashboard when the page loads
// let dashboard;
// document.addEventListener('DOMContentLoaded', () => {
//     dashboard = new VehicleDashboard();
//     // Expose globally for table actions
//     window.dashboard = dashboard;
// });

// // Handle page unload
// window.addEventListener('beforeunload', () => {
//     if (dashboard) {
//         dashboard.destroy();
//     }
// });