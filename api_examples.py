"""
Django IoT Dashboard - API Examples (Python)
ตัวอย่างการใช้งาน REST API ด้วย Python requests
"""

import requests
import json
import time

# ========================================
# Configuration
# ========================================
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"


# ========================================
# LED Control Functions
# ========================================

def get_led_status():
    """Get current LED status"""
    try:
        response = requests.get(f"{API_V1}/led/")
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


def control_led(command):
    """
    Control LED
    command: 'ON', 'OFF', or 'TOGGLE'
    """
    try:
        response = requests.post(
            f"{API_V1}/led/",
            json={"command": command},
            headers={"Content-Type": "application/json"}
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


# ========================================
# Relay Control Functions
# ========================================

def get_relay_status():
    """Get status of all relays"""
    try:
        response = requests.get(f"{API_V1}/relay/")
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


def control_relay(relay_num, command):
    """
    Control specific relay
    relay_num: 1, 2, or 3
    command: 'ON', 'OFF', or 'TOGGLE'
    """
    try:
        response = requests.post(
            f"{API_V1}/relay/",
            json={
                "relay_num": relay_num,
                "command": command
            },
            headers={"Content-Type": "application/json"}
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


# ========================================
# Sensor Data Functions
# ========================================

def get_latest_sensor():
    """Get latest sensor reading"""
    try:
        response = requests.get(f"{API_V1}/sensors/latest/")
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_sensor_list(limit=20, offset=0):
    """
    Get sensor data list with pagination
    limit: number of items per page
    offset: starting position
    """
    try:
        response = requests.get(
            f"{API_V1}/sensors/",
            params={"limit": limit, "offset": offset}
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_sensor_stats():
    """Get sensor data statistics"""
    try:
        response = requests.get(f"{API_V1}/sensors/stats/")
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_sensor_data(temperature, humidity, device_name="API_Test"):
    """Create new sensor data entry"""
    try:
        response = requests.post(
            f"{API_V1}/sensors/",
            json={
                "temperature": temperature,
                "humidity": humidity,
                "device_name": device_name
            },
            headers={"Content-Type": "application/json"}
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_sensor_by_id(sensor_id):
    """Get specific sensor data by ID"""
    try:
        response = requests.get(f"{API_V1}/sensors/{sensor_id}/")
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


def update_sensor_data(sensor_id, temperature=None, humidity=None, device_name=None):
    """Update sensor data (partial update)"""
    try:
        data = {}
        if temperature is not None:
            data["temperature"] = temperature
        if humidity is not None:
            data["humidity"] = humidity
        if device_name is not None:
            data["device_name"] = device_name
        
        response = requests.patch(
            f"{API_V1}/sensors/{sensor_id}/",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_sensor_data(sensor_id):
    """Delete sensor data by ID"""
    try:
        response = requests.delete(f"{API_V1}/sensors/{sensor_id}/")
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


# ========================================
# System Status Functions
# ========================================

def get_system_status():
    """Get complete system status"""
    try:
        response = requests.get(f"{API_V1}/system/status/")
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


# ========================================
# Example Usage
# ========================================

def main():
    print("=" * 60)
    print("Django IoT Dashboard - API Examples")
    print("=" * 60)
    print()
    
    # Example 1: Get System Status
    print("📊 Example 1: Get System Status")
    print("-" * 60)
    result = get_system_status()
    if result.get('success'):
        print(json.dumps(result['data'], indent=2))
    else:
        print(f"Error: {result.get('error')}")
    print()
    
    # Example 2: Control LED
    print("💡 Example 2: Control LED")
    print("-" * 60)
    
    # Turn ON
    print("→ Turning LED ON...")
    result = control_led('ON')
    print(f"  Status: {result.get('message', result.get('error'))}")
    time.sleep(1)
    
    # Check status
    result = get_led_status()
    if result.get('success'):
        print(f"  LED is now: {'ON 🟢' if result['data']['is_on'] else 'OFF ⚫'}")
    time.sleep(2)
    
    # Turn OFF
    print("→ Turning LED OFF...")
    result = control_led('OFF')
    print(f"  Status: {result.get('message', result.get('error'))}")
    print()
    
    # Example 3: Control Relays
    print("⚡ Example 3: Control Relays")
    print("-" * 60)
    
    # Turn ON Relay 1
    print("→ Turning Relay 1 ON...")
    result = control_relay(1, 'ON')
    print(f"  Status: {result.get('message', result.get('error'))}")
    time.sleep(1)
    
    # Turn ON Relay 2
    print("→ Turning Relay 2 ON...")
    result = control_relay(2, 'ON')
    print(f"  Status: {result.get('message', result.get('error'))}")
    time.sleep(1)
    
    # Check all relays
    result = get_relay_status()
    if result.get('success'):
        data = result['data']
        print(f"  Relay 1: {'ON 🟢' if data['relay1'] else 'OFF ⚫'}")
        print(f"  Relay 2: {'ON 🟢' if data['relay2'] else 'OFF ⚫'}")
        print(f"  Relay 3: {'ON 🟢' if data['relay3'] else 'OFF ⚫'}")
    time.sleep(1)
    
    # Turn OFF all relays
    print("→ Turning all relays OFF...")
    control_relay(1, 'OFF')
    control_relay(2, 'OFF')
    control_relay(3, 'OFF')
    print("  All relays turned OFF")
    print()
    
    # Example 4: Sensor Data
    print("🌡️  Example 4: Sensor Data Management")
    print("-" * 60)
    
    # Get latest sensor
    print("→ Getting latest sensor data...")
    result = get_latest_sensor()
    if result.get('success') and result['data']:
        data = result['data']
        print(f"  Temperature: {data['temperature']}°C")
        print(f"  Humidity: {data['humidity']}%")
        print(f"  Time: {data['timestamp']}")
    else:
        print("  No sensor data available")
    print()
    
    # Create test sensor data
    print("→ Creating test sensor data...")
    result = create_sensor_data(
        temperature=28.5,
        humidity=65.3,
        device_name="Python_API_Test"
    )
    if result.get('success'):
        sensor_id = result['data']['id']
        print(f"  Created sensor ID: {sensor_id}")
        print(f"  Temperature: {result['data']['temperature']}°C")
        print(f"  Humidity: {result['data']['humidity']}%")
        
        # Update the sensor data
        time.sleep(1)
        print(f"→ Updating sensor {sensor_id}...")
        result = update_sensor_data(sensor_id, temperature=29.0)
        if result.get('success'):
            print(f"  Updated temperature to: {result['data']['temperature']}°C")
        
        # Delete the sensor data
        time.sleep(1)
        print(f"→ Deleting sensor {sensor_id}...")
        result = delete_sensor_data(sensor_id)
        if result.get('success'):
            print(f"  Deleted successfully")
    print()
    
    # Example 5: Get Statistics
    print("📈 Example 5: Sensor Statistics")
    print("-" * 60)
    result = get_sensor_stats()
    if result.get('success'):
        stats = result['data']
        print(f"  Total Readings: {stats['total_readings']}")
        print(f"  Temperature:")
        print(f"    - Average: {stats['temperature']['average']}°C")
        print(f"    - Max: {stats['temperature']['max']}°C")
        print(f"    - Min: {stats['temperature']['min']}°C")
        print(f"  Humidity:")
        print(f"    - Average: {stats['humidity']['average']}%")
        print(f"    - Max: {stats['humidity']['max']}%")
        print(f"    - Min: {stats['humidity']['min']}%")
    print()
    
    # Example 6: Get Sensor List with Pagination
    print("📋 Example 6: Get Sensor List (Pagination)")
    print("-" * 60)
    result = get_sensor_list(limit=5, offset=0)
    if result.get('success'):
        print(f"  Total: {result['pagination']['total']}")
        print(f"  Showing: {result['pagination']['count']} items")
        print(f"  Latest 5 readings:")
        for sensor in result['data']:
            print(f"    - ID {sensor['id']}: {sensor['temperature']}°C, {sensor['humidity']}% @ {sensor['timestamp']}")
    print()
    
    print("=" * 60)
    print("✅ All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
