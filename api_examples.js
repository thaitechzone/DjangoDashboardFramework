/*
 * Django IoT Dashboard - API Examples (JavaScript)
 * ตัวอย่างการใช้งาน REST API ด้วย JavaScript fetch
 */

// ========================================
// Configuration
// ========================================
const BASE_URL = 'http://localhost:8000';
const API_V1 = `${BASE_URL}/api/v1`;

// ========================================
// Helper Functions
// ========================================

async function apiRequest(url, method = 'GET', body = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (body) {
        options.body = JSON.stringify(body);
    }
    
    try {
        const response = await fetch(url, options);
        const data = await response.json();
        return data;
    } catch (error) {
        return {
            success: false,
            error: error.message
        };
    }
}

// ========================================
// LED Control Functions
// ========================================

async function getLedStatus() {
    return await apiRequest(`${API_V1}/led/`);
}

async function controlLed(command) {
    // command: 'ON', 'OFF', or 'TOGGLE'
    return await apiRequest(`${API_V1}/led/`, 'POST', { command });
}

// ========================================
// Relay Control Functions
// ========================================

async function getRelayStatus() {
    return await apiRequest(`${API_V1}/relay/`);
}

async function controlRelay(relay_num, command) {
    // relay_num: 1, 2, or 3
    // command: 'ON', 'OFF', or 'TOGGLE'
    return await apiRequest(`${API_V1}/relay/`, 'POST', {
        relay_num,
        command
    });
}

// ========================================
// Sensor Data Functions
// ========================================

async function getLatestSensor() {
    return await apiRequest(`${API_V1}/sensors/latest/`);
}

async function getSensorList(limit = 20, offset = 0) {
    return await apiRequest(`${API_V1}/sensors/?limit=${limit}&offset=${offset}`);
}

async function getSensorStats() {
    return await apiRequest(`${API_V1}/sensors/stats/`);
}

async function createSensorData(temperature, humidity, device_name = 'JS_API_Test') {
    return await apiRequest(`${API_V1}/sensors/`, 'POST', {
        temperature,
        humidity,
        device_name
    });
}

async function getSensorById(sensor_id) {
    return await apiRequest(`${API_V1}/sensors/${sensor_id}/`);
}

async function updateSensorData(sensor_id, data) {
    return await apiRequest(`${API_V1}/sensors/${sensor_id}/`, 'PATCH', data);
}

async function deleteSensorData(sensor_id) {
    return await apiRequest(`${API_V1}/sensors/${sensor_id}/`, 'DELETE');
}

// ========================================
// System Status Functions
// ========================================

async function getSystemStatus() {
    return await apiRequest(`${API_V1}/system/status/`);
}

// ========================================
// Example Usage
// ========================================

async function runExamples() {
    console.log('='.repeat(60));
    console.log('Django IoT Dashboard - API Examples (JavaScript)');
    console.log('='.repeat(60));
    console.log('');
    
    // Example 1: Get System Status
    console.log('📊 Example 1: Get System Status');
    console.log('-'.repeat(60));
    let result = await getSystemStatus();
    if (result.success) {
        console.log(JSON.stringify(result.data, null, 2));
    } else {
        console.log(`Error: ${result.error}`);
    }
    console.log('');
    
    // Example 2: Control LED
    console.log('💡 Example 2: Control LED');
    console.log('-'.repeat(60));
    
    // Turn ON
    console.log('→ Turning LED ON...');
    result = await controlLed('ON');
    console.log(`  Status: ${result.message || result.error}`);
    await sleep(1000);
    
    // Check status
    result = await getLedStatus();
    if (result.success) {
        console.log(`  LED is now: ${result.data.is_on ? 'ON 🟢' : 'OFF ⚫'}`);
    }
    await sleep(2000);
    
    // Turn OFF
    console.log('→ Turning LED OFF...');
    result = await controlLed('OFF');
    console.log(`  Status: ${result.message || result.error}`);
    console.log('');
    
    // Example 3: Control Relays
    console.log('⚡ Example 3: Control Relays');
    console.log('-'.repeat(60));
    
    // Turn ON Relay 1
    console.log('→ Turning Relay 1 ON...');
    result = await controlRelay(1, 'ON');
    console.log(`  Status: ${result.message || result.error}`);
    await sleep(1000);
    
    // Turn ON Relay 2
    console.log('→ Turning Relay 2 ON...');
    result = await controlRelay(2, 'ON');
    console.log(`  Status: ${result.message || result.error}`);
    await sleep(1000);
    
    // Check all relays
    result = await getRelayStatus();
    if (result.success) {
        const data = result.data;
        console.log(`  Relay 1: ${data.relay1 ? 'ON 🟢' : 'OFF ⚫'}`);
        console.log(`  Relay 2: ${data.relay2 ? 'ON 🟢' : 'OFF ⚫'}`);
        console.log(`  Relay 3: ${data.relay3 ? 'ON 🟢' : 'OFF ⚫'}`);
    }
    await sleep(1000);
    
    // Turn OFF all relays
    console.log('→ Turning all relays OFF...');
    await controlRelay(1, 'OFF');
    await controlRelay(2, 'OFF');
    await controlRelay(3, 'OFF');
    console.log('  All relays turned OFF');
    console.log('');
    
    // Example 4: Sensor Data
    console.log('🌡️  Example 4: Sensor Data Management');
    console.log('-'.repeat(60));
    
    // Get latest sensor
    console.log('→ Getting latest sensor data...');
    result = await getLatestSensor();
    if (result.success && result.data) {
        const data = result.data;
        console.log(`  Temperature: ${data.temperature}°C`);
        console.log(`  Humidity: ${data.humidity}%`);
        console.log(`  Time: ${data.timestamp}`);
    } else {
        console.log('  No sensor data available');
    }
    console.log('');
    
    // Create test sensor data
    console.log('→ Creating test sensor data...');
    result = await createSensorData(28.5, 65.3, 'JS_API_Test');
    if (result.success) {
        const sensor_id = result.data.id;
        console.log(`  Created sensor ID: ${sensor_id}`);
        console.log(`  Temperature: ${result.data.temperature}°C`);
        console.log(`  Humidity: ${result.data.humidity}%`);
        
        // Update the sensor data
        await sleep(1000);
        console.log(`→ Updating sensor ${sensor_id}...`);
        result = await updateSensorData(sensor_id, { temperature: 29.0 });
        if (result.success) {
            console.log(`  Updated temperature to: ${result.data.temperature}°C`);
        }
        
        // Delete the sensor data
        await sleep(1000);
        console.log(`→ Deleting sensor ${sensor_id}...`);
        result = await deleteSensorData(sensor_id);
        if (result.success) {
            console.log('  Deleted successfully');
        }
    }
    console.log('');
    
    // Example 5: Get Statistics
    console.log('📈 Example 5: Sensor Statistics');
    console.log('-'.repeat(60));
    result = await getSensorStats();
    if (result.success) {
        const stats = result.data;
        console.log(`  Total Readings: ${stats.total_readings}`);
        console.log('  Temperature:');
        console.log(`    - Average: ${stats.temperature.average}°C`);
        console.log(`    - Max: ${stats.temperature.max}°C`);
        console.log(`    - Min: ${stats.temperature.min}°C`);
        console.log('  Humidity:');
        console.log(`    - Average: ${stats.humidity.average}%`);
        console.log(`    - Max: ${stats.humidity.max}%`);
        console.log(`    - Min: ${stats.humidity.min}%`);
    }
    console.log('');
    
    // Example 6: Get Sensor List with Pagination
    console.log('📋 Example 6: Get Sensor List (Pagination)');
    console.log('-'.repeat(60));
    result = await getSensorList(5, 0);
    if (result.success) {
        console.log(`  Total: ${result.pagination.total}`);
        console.log(`  Showing: ${result.pagination.count} items`);
        console.log('  Latest 5 readings:');
        result.data.forEach(sensor => {
            console.log(`    - ID ${sensor.id}: ${sensor.temperature}°C, ${sensor.humidity}% @ ${sensor.timestamp}`);
        });
    }
    console.log('');
    
    console.log('='.repeat(60));
    console.log('✅ All examples completed!');
    console.log('='.repeat(60));
}

// Helper sleep function
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// ========================================
// Browser Usage (add to HTML)
// ========================================

/*
<!DOCTYPE html>
<html>
<head>
    <title>Django IoT Dashboard API Test</title>
</head>
<body>
    <h1>Django IoT Dashboard API Test</h1>
    
    <div>
        <h2>LED Control</h2>
        <button onclick="controlLed('ON')">Turn ON</button>
        <button onclick="controlLed('OFF')">Turn OFF</button>
        <button onclick="controlLed('TOGGLE')">Toggle</button>
        <button onclick="showLedStatus()">Get Status</button>
        <div id="led-status"></div>
    </div>
    
    <div>
        <h2>Relay Control</h2>
        <div>
            <h3>Relay 1</h3>
            <button onclick="controlRelay(1, 'ON')">ON</button>
            <button onclick="controlRelay(1, 'OFF')">OFF</button>
            <button onclick="controlRelay(1, 'TOGGLE')">Toggle</button>
        </div>
        <div>
            <h3>Relay 2</h3>
            <button onclick="controlRelay(2, 'ON')">ON</button>
            <button onclick="controlRelay(2, 'OFF')">OFF</button>
            <button onclick="controlRelay(2, 'TOGGLE')">Toggle</button>
        </div>
        <div>
            <h3>Relay 3</h3>
            <button onclick="controlRelay(3, 'ON')">ON</button>
            <button onclick="controlRelay(3, 'OFF')">OFF</button>
            <button onclick="controlRelay(3, 'TOGGLE')">Toggle</button>
        </div>
        <button onclick="showRelayStatus()">Get All Status</button>
        <div id="relay-status"></div>
    </div>
    
    <div>
        <h2>Sensor Data</h2>
        <button onclick="showLatestSensor()">Get Latest</button>
        <button onclick="showSensorStats()">Get Stats</button>
        <button onclick="createTestSensor()">Create Test Data</button>
        <div id="sensor-data"></div>
    </div>
    
    <div>
        <h2>System Status</h2>
        <button onclick="showSystemStatus()">Get System Status</button>
        <div id="system-status"></div>
    </div>
    
    <script src="api_examples.js"></script>
    <script>
        async function showLedStatus() {
            const result = await getLedStatus();
            document.getElementById('led-status').innerHTML = 
                `<pre>${JSON.stringify(result, null, 2)}</pre>`;
        }
        
        async function showRelayStatus() {
            const result = await getRelayStatus();
            document.getElementById('relay-status').innerHTML = 
                `<pre>${JSON.stringify(result, null, 2)}</pre>`;
        }
        
        async function showLatestSensor() {
            const result = await getLatestSensor();
            document.getElementById('sensor-data').innerHTML = 
                `<pre>${JSON.stringify(result, null, 2)}</pre>`;
        }
        
        async function showSensorStats() {
            const result = await getSensorStats();
            document.getElementById('sensor-data').innerHTML = 
                `<pre>${JSON.stringify(result, null, 2)}</pre>`;
        }
        
        async function createTestSensor() {
            const result = await createSensorData(28.5, 65.3, 'Browser_Test');
            document.getElementById('sensor-data').innerHTML = 
                `<pre>${JSON.stringify(result, null, 2)}</pre>`;
        }
        
        async function showSystemStatus() {
            const result = await getSystemStatus();
            document.getElementById('system-status').innerHTML = 
                `<pre>${JSON.stringify(result, null, 2)}</pre>`;
        }
    </script>
</body>
</html>
*/

// ========================================
// Node.js Usage
// ========================================

// For Node.js, install node-fetch first:
// npm install node-fetch
// 
// Then add at the top:
// const fetch = require('node-fetch');
//
// Run with:
// node api_examples.js

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getLedStatus,
        controlLed,
        getRelayStatus,
        controlRelay,
        getLatestSensor,
        getSensorList,
        getSensorStats,
        createSensorData,
        getSensorById,
        updateSensorData,
        deleteSensorData,
        getSystemStatus,
        runExamples
    };
}
