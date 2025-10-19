/*
 * ESP32 RELAY Controller with MQTT - Full Code
 * 
 * ควบคุม RELAY 3 ช่องผ่าน MQTT
 * รองรับการรับคำสั่งจาก Dashboard และส่งสถานะกลับ
 * 
 * Topics:
 * - Control (รับคำสั่ง): thaitechzone/v2_board/control/relay[1,2,3]
 * - State (ส่งสถานะ): thaitechzone/v2_board/state/relay[1,2,3]
 * 
 * Payload: ON/OFF
 */

#include <WiFi.h>
#include <PubSubClient.h>

// WiFi Configuration
const char* WIFI_SSID = "YOUR_WIFI_SSID";        // 🔴 เปลี่ยนเป็น WiFi ของคุณ
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"; // 🔴 เปลี่ยนเป็น Password ของคุณ

// MQTT Configuration
const char* MQTT_BROKER = "broker.hivemq.com";
const int MQTT_PORT = 1883;
const char* MQTT_CLIENT_ID = "ESP32_RELAY_Controller";  // เปลี่ยนได้ถ้าต้องการ

// MQTT Topics - Control (รับคำสั่งจาก Dashboard)
const char* RELAY1_CONTROL_TOPIC = "thaitechzone/v2_board/control/relay1";
const char* RELAY2_CONTROL_TOPIC = "thaitechzone/v2_board/control/relay2";
const char* RELAY3_CONTROL_TOPIC = "thaitechzone/v2_board/control/relay3";

// MQTT Topics - State (ส่งสถานะกลับไป Dashboard)
const char* RELAY1_STATE_TOPIC = "thaitechzone/v2_board/state/relay1";
const char* RELAY2_STATE_TOPIC = "thaitechzone/v2_board/state/relay2";
const char* RELAY3_STATE_TOPIC = "thaitechzone/v2_board/state/relay3";

// GPIO Pins สำหรับ RELAY
const int RELAY1_PIN = 25;  // 🔴 เปลี่ยนตาม board ของคุณ
const int RELAY2_PIN = 26;  // 🔴 เปลี่ยนตาม board ของคุณ
const int RELAY3_PIN = 27;  // 🔴 เปลี่ยนตาม board ของคุณ

// สถานะของ RELAY
bool relay1_state = false;
bool relay2_state = false;
bool relay3_state = false;

// WiFi และ MQTT clients
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

// ========================================
// Setup Functions
// ========================================

void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("\n\n🚀 ESP32 RELAY Controller Starting...");
    Serial.println("========================================");
    
    // ตั้งค่า GPIO pins
    setupGPIO();
    
    // เชื่อมต่อ WiFi
    connectWiFi();
    
    // ตั้งค่า MQTT
    mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
    mqttClient.setCallback(mqttCallback);
    
    // เชื่อมต่อ MQTT
    connectMQTT();
    
    Serial.println("✅ System Ready!");
    Serial.println("========================================\n");
}

void setupGPIO() {
    Serial.println("🔧 Setting up GPIO pins...");
    
    // ตั้งค่า relay pins เป็น OUTPUT
    pinMode(RELAY1_PIN, OUTPUT);
    pinMode(RELAY2_PIN, OUTPUT);
    pinMode(RELAY3_PIN, OUTPUT);
    
    // เริ่มต้นเป็น OFF (LOW)
    digitalWrite(RELAY1_PIN, LOW);
    digitalWrite(RELAY2_PIN, LOW);
    digitalWrite(RELAY3_PIN, LOW);
    
    Serial.println("   ✓ RELAY 1 Pin: " + String(RELAY1_PIN));
    Serial.println("   ✓ RELAY 2 Pin: " + String(RELAY2_PIN));
    Serial.println("   ✓ RELAY 3 Pin: " + String(RELAY3_PIN));
}

// ========================================
// WiFi Functions
// ========================================

void connectWiFi() {
    Serial.println("📶 Connecting to WiFi: " + String(WIFI_SSID));
    
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n✅ WiFi Connected!");
        Serial.println("   IP Address: " + WiFi.localIP().toString());
        Serial.println("   Signal: " + String(WiFi.RSSI()) + " dBm");
    } else {
        Serial.println("\n❌ WiFi Connection Failed!");
        Serial.println("⚠️  Please check SSID and password");
    }
}

// ========================================
// MQTT Functions
// ========================================

void connectMQTT() {
    Serial.println("📡 Connecting to MQTT Broker: " + String(MQTT_BROKER));
    
    int attempts = 0;
    while (!mqttClient.connected() && attempts < 5) {
        Serial.print("   Attempt " + String(attempts + 1) + "...");
        
        if (mqttClient.connect(MQTT_CLIENT_ID)) {
            Serial.println(" Connected!");
            
            // Subscribe to control topics
            subscribeToTopics();
            
            // Publish initial states
            publishAllStates();
            
        } else {
            Serial.println(" Failed! (rc=" + String(mqttClient.state()) + ")");
            delay(2000);
        }
        attempts++;
    }
    
    if (!mqttClient.connected()) {
        Serial.println("❌ MQTT Connection Failed after " + String(attempts) + " attempts");
    }
}

void subscribeToTopics() {
    Serial.println("📥 Subscribing to control topics...");
    
    mqttClient.subscribe(RELAY1_CONTROL_TOPIC);
    Serial.println("   ✓ " + String(RELAY1_CONTROL_TOPIC));
    
    mqttClient.subscribe(RELAY2_CONTROL_TOPIC);
    Serial.println("   ✓ " + String(RELAY2_CONTROL_TOPIC));
    
    mqttClient.subscribe(RELAY3_CONTROL_TOPIC);
    Serial.println("   ✓ " + String(RELAY3_CONTROL_TOPIC));
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    // แปลง payload เป็น String
    String message = "";
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    Serial.println("\n📨 MQTT Message Received:");
    Serial.println("   Topic: " + String(topic));
    Serial.println("   Message: " + message);
    
    // จัดการคำสั่ง RELAY 1
    if (String(topic) == RELAY1_CONTROL_TOPIC) {
        handleRelayCommand(1, message);
    }
    // จัดการคำสั่ง RELAY 2
    else if (String(topic) == RELAY2_CONTROL_TOPIC) {
        handleRelayCommand(2, message);
    }
    // จัดการคำสั่ง RELAY 3
    else if (String(topic) == RELAY3_CONTROL_TOPIC) {
        handleRelayCommand(3, message);
    }
}

void handleRelayCommand(int relayNum, String command) {
    bool newState = false;
    int pin = 0;
    
    // กำหนด pin และ state variable
    if (relayNum == 1) {
        pin = RELAY1_PIN;
    } else if (relayNum == 2) {
        pin = RELAY2_PIN;
    } else if (relayNum == 3) {
        pin = RELAY3_PIN;
    }
    
    // ประมวลผลคำสั่ง
    if (command == "ON") {
        newState = true;
        digitalWrite(pin, HIGH);
        Serial.println("   ✅ RELAY " + String(relayNum) + " turned ON");
    } 
    else if (command == "OFF") {
        newState = false;
        digitalWrite(pin, LOW);
        Serial.println("   ✅ RELAY " + String(relayNum) + " turned OFF");
    } 
    else {
        Serial.println("   ⚠️  Unknown command: " + command);
        return;
    }
    
    // อัปเดตสถานะ
    if (relayNum == 1) relay1_state = newState;
    else if (relayNum == 2) relay2_state = newState;
    else if (relayNum == 3) relay3_state = newState;
    
    // ส่งสถานะกลับไป Dashboard
    publishRelayState(relayNum, newState);
}

void publishRelayState(int relayNum, bool state) {
    String topic = "";
    String payload = state ? "ON" : "OFF";
    
    // เลือก topic ตามหมายเลข relay
    if (relayNum == 1) {
        topic = RELAY1_STATE_TOPIC;
    } else if (relayNum == 2) {
        topic = RELAY2_STATE_TOPIC;
    } else if (relayNum == 3) {
        topic = RELAY3_STATE_TOPIC;
    }
    
    // Publish state
    bool success = mqttClient.publish(topic.c_str(), payload.c_str());
    
    if (success) {
        Serial.println("   📤 State published: " + topic + " = " + payload);
    } else {
        Serial.println("   ❌ Failed to publish state");
    }
}

void publishAllStates() {
    Serial.println("📤 Publishing initial states...");
    publishRelayState(1, relay1_state);
    publishRelayState(2, relay2_state);
    publishRelayState(3, relay3_state);
}

// ========================================
// Main Loop
// ========================================

void loop() {
    // ตรวจสอบ WiFi
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("⚠️  WiFi disconnected! Reconnecting...");
        connectWiFi();
    }
    
    // ตรวจสอบ MQTT
    if (!mqttClient.connected()) {
        Serial.println("⚠️  MQTT disconnected! Reconnecting...");
        connectMQTT();
    }
    
    // ประมวลผล MQTT
    mqttClient.loop();
    
    // Delay เล็กน้อยเพื่อประหยัดพลังงาน
    delay(10);
}

// ========================================
// Optional: Manual Control Functions
// ========================================

// ถ้าต้องการควบคุม relay ด้วยปุ่มกด หรือ condition อื่นๆ
void setRelay(int relayNum, bool state) {
    int pin = 0;
    
    if (relayNum == 1) {
        pin = RELAY1_PIN;
        relay1_state = state;
    } else if (relayNum == 2) {
        pin = RELAY2_PIN;
        relay2_state = state;
    } else if (relayNum == 3) {
        pin = RELAY3_PIN;
        relay3_state = state;
    }
    
    digitalWrite(pin, state ? HIGH : LOW);
    publishRelayState(relayNum, state);
    
    Serial.println("🔧 Manual: RELAY " + String(relayNum) + " = " + (state ? "ON" : "OFF"));
}

// ตัวอย่างการใช้:
// setRelay(1, true);  // เปิด RELAY 1
// setRelay(2, false); // ปิด RELAY 2
