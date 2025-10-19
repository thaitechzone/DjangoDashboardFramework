// ESP32 RELAY Control Example Code
// สำหรับควบคุม RELAY 3 ช่องผ่าน MQTT

#include <WiFi.h>
#include <PubSubClient.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// MQTT Broker settings
const char* mqtt_broker = "YOUR_MQTT_BROKER_IP";
const int mqtt_port = 1883;
const char* mqtt_username = "YOUR_USERNAME";  // ถ้ามี
const char* mqtt_password = "YOUR_PASSWORD";  // ถ้ามี

// MQTT Topics
const char* topic_relay1_control = "thaitechzone/v2_board/control/relay1";
const char* topic_relay2_control = "thaitechzone/v2_board/control/relay2";
const char* topic_relay3_control = "thaitechzone/v2_board/control/relay3";

const char* topic_relay1_state = "thaitechzone/v2_board/state/relay1";
const char* topic_relay2_state = "thaitechzone/v2_board/state/relay2";
const char* topic_relay3_state = "thaitechzone/v2_board/state/relay3";

// GPIO Pins สำหรับ RELAY
#define RELAY1_PIN 25
#define RELAY2_PIN 26
#define RELAY3_PIN 27

// LED Onboard สำหรับ debug
#define LED_PIN 2

// ตัวแปรเก็บสถานะ RELAY
bool relay1_state = false;
bool relay2_state = false;
bool relay3_state = false;

// WiFi และ MQTT Client
WiFiClient espClient;
PubSubClient mqttClient(espClient);

// Function Declarations
void connectWiFi();
void connectMQTT();
void mqttCallback(char* topic, byte* payload, unsigned int length);
void publishRelayStatus(int relayNum, bool state);
void controlRelay(int relayNum, bool state);

void setup() {
    Serial.begin(115200);
    Serial.println("\n\n🚀 ESP32 RELAY Controller Starting...");
    
    // ตั้งค่า GPIO Pins
    pinMode(RELAY1_PIN, OUTPUT);
    pinMode(RELAY2_PIN, OUTPUT);
    pinMode(RELAY3_PIN, OUTPUT);
    pinMode(LED_PIN, OUTPUT);
    
    // ปิด RELAY ทั้งหมดตอนเริ่มต้น
    digitalWrite(RELAY1_PIN, LOW);
    digitalWrite(RELAY2_PIN, LOW);
    digitalWrite(RELAY3_PIN, LOW);
    digitalWrite(LED_PIN, LOW);
    
    Serial.println("✅ GPIO Pins Initialized");
    
    // เชื่อมต่อ WiFi
    connectWiFi();
    
    // ตั้งค่า MQTT
    mqttClient.setServer(mqtt_broker, mqtt_port);
    mqttClient.setCallback(mqttCallback);
    
    // เชื่อมต่อ MQTT
    connectMQTT();
    
    Serial.println("✅ Setup Complete!");
}

void loop() {
    // ตรวจสอบการเชื่อมต่อ WiFi
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("❌ WiFi Disconnected! Reconnecting...");
        connectWiFi();
    }
    
    // ตรวจสอบการเชื่อมต่อ MQTT
    if (!mqttClient.connected()) {
        Serial.println("❌ MQTT Disconnected! Reconnecting...");
        connectMQTT();
    }
    
    // ให้ MQTT client ประมวลผล
    mqttClient.loop();
    
    // ส่งสถานะ RELAY ทุกๆ 30 วินาที
    static unsigned long lastStatusUpdate = 0;
    if (millis() - lastStatusUpdate > 30000) {
        Serial.println("\n📤 Sending periodic status update...");
        publishRelayStatus(1, relay1_state);
        delay(100);
        publishRelayStatus(2, relay2_state);
        delay(100);
        publishRelayStatus(3, relay3_state);
        lastStatusUpdate = millis();
    }
    
    // Blink LED เพื่อแสดงว่าระบบทำงาน
    static unsigned long lastBlink = 0;
    if (millis() - lastBlink > 2000) {
        digitalWrite(LED_PIN, !digitalRead(LED_PIN));
        lastBlink = millis();
    }
    
    delay(100);
}

void connectWiFi() {
    Serial.print("📡 Connecting to WiFi: ");
    Serial.println(ssid);
    
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n✅ WiFi Connected!");
        Serial.print("📍 IP Address: ");
        Serial.println(WiFi.localIP());
        Serial.print("📶 Signal Strength: ");
        Serial.print(WiFi.RSSI());
        Serial.println(" dBm");
    } else {
        Serial.println("\n❌ WiFi Connection Failed!");
    }
}

void connectMQTT() {
    while (!mqttClient.connected()) {
        Serial.print("📡 Connecting to MQTT Broker: ");
        Serial.println(mqtt_broker);
        
        String clientId = "ESP32_RELAY_" + String(WiFi.macAddress());
        
        // ลองเชื่อมต่อ MQTT
        bool connected;
        if (mqtt_username && mqtt_password) {
            connected = mqttClient.connect(clientId.c_str(), mqtt_username, mqtt_password);
        } else {
            connected = mqttClient.connect(clientId.c_str());
        }
        
        if (connected) {
            Serial.println("✅ MQTT Connected!");
            
            // Subscribe MQTT Topics
            Serial.println("\n📥 Subscribing to topics...");
            mqttClient.subscribe(topic_relay1_control);
            Serial.println("  ✓ " + String(topic_relay1_control));
            
            mqttClient.subscribe(topic_relay2_control);
            Serial.println("  ✓ " + String(topic_relay2_control));
            
            mqttClient.subscribe(topic_relay3_control);
            Serial.println("  ✓ " + String(topic_relay3_control));
            
            // ส่งสถานะเริ่มต้น
            Serial.println("\n📤 Publishing initial status...");
            publishRelayStatus(1, relay1_state);
            delay(100);
            publishRelayStatus(2, relay2_state);
            delay(100);
            publishRelayStatus(3, relay3_state);
            
        } else {
            Serial.print("❌ MQTT Connection Failed! RC=");
            Serial.println(mqttClient.state());
            Serial.println("⏳ Retrying in 5 seconds...");
            delay(5000);
        }
    }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    // แปลง payload เป็น String
    String message = "";
    for (unsigned int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    // แสดง log
    Serial.println("\n📨 ===== MQTT Message Received =====");
    Serial.print("📌 Topic: ");
    Serial.println(topic);
    Serial.print("💬 Payload: ");
    Serial.println(message);
    
    String topicStr = String(topic);
    
    // ควบคุม RELAY 1
    if (topicStr == topic_relay1_control) {
        if (message == "ON") {
            controlRelay(1, true);
        } else if (message == "OFF") {
            controlRelay(1, false);
        }
        publishRelayStatus(1, relay1_state);
    }
    
    // ควบคุม RELAY 2
    else if (topicStr == topic_relay2_control) {
        if (message == "ON") {
            controlRelay(2, true);
        } else if (message == "OFF") {
            controlRelay(2, false);
        }
        publishRelayStatus(2, relay2_state);
    }
    
    // ควบคุม RELAY 3
    else if (topicStr == topic_relay3_control) {
        if (message == "ON") {
            controlRelay(3, true);
        } else if (message == "OFF") {
            controlRelay(3, false);
        }
        publishRelayStatus(3, relay3_state);
    }
    
    Serial.println("===================================\n");
}

void controlRelay(int relayNum, bool state) {
    int pin;
    bool* stateVar;
    
    // เลือก pin และตัวแปรสถานะ
    switch(relayNum) {
        case 1:
            pin = RELAY1_PIN;
            stateVar = &relay1_state;
            break;
        case 2:
            pin = RELAY2_PIN;
            stateVar = &relay2_state;
            break;
        case 3:
            pin = RELAY3_PIN;
            stateVar = &relay3_state;
            break;
        default:
            Serial.println("❌ Invalid relay number!");
            return;
    }
    
    // ควบคุม RELAY
    digitalWrite(pin, state ? HIGH : LOW);
    *stateVar = state;
    
    // แสดง log
    Serial.print(state ? "🟢 " : "⚫ ");
    Serial.print("RELAY ");
    Serial.print(relayNum);
    Serial.println(state ? " ON" : " OFF");
}

void publishRelayStatus(int relayNum, bool state) {
    const char* topic;
    
    // เลือก topic
    switch(relayNum) {
        case 1:
            topic = topic_relay1_state;
            break;
        case 2:
            topic = topic_relay2_state;
            break;
        case 3:
            topic = topic_relay3_state;
            break;
        default:
            Serial.println("❌ Invalid relay number for publish!");
            return;
    }
    
    // ส่งสถานะ
    String payload = state ? "ON" : "OFF";
    bool success = mqttClient.publish(topic, payload.c_str());
    
    if (success) {
        Serial.print("📤 Published: ");
        Serial.print(topic);
        Serial.print(" = ");
        Serial.println(payload);
    } else {
        Serial.print("❌ Publish Failed: ");
        Serial.println(topic);
    }
}
