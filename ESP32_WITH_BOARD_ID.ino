/*
 * ESP32 IoT Dashboard Controller with Board ID Support
 * ======================================================
 * 
 * Features:
 * - Dynamic Board ID configuration
 * - LED control (onboard)
 * - 3 Relay channels control
 * - DHT22 Temperature & Humidity sensor
 * - MQTT communication with unique topics per board
 * 
 * Compatible with: Django IoT Dashboard Framework v2.0+
 * Author: ThaiTechZone
 * Updated: October 2025
 */

#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// ===== Board Configuration =====
// 🔥 IMPORTANT: Change this to a unique ID for each ESP32 board
const char* BOARD_ID = "board_01";  // Examples: "living_room", "bedroom", "greenhouse_1"

// ===== Pin Definitions =====
#define LED_PIN 2           // Onboard LED (GPIO2) - Active High
#define DHT_PIN 15          // DHT sensor pin (GPIO15)
#define DHT_TYPE DHT22      // DHT22 (AM2302)
#define RELAY1_PIN 17       // Relay 1 pin (GPIO17)
#define RELAY2_PIN 16       // Relay 2 pin (GPIO16)
#define RELAY3_PIN 4        // Relay 3 pin (GPIO4)

// ===== WiFi Configuration =====
// 🔥 IMPORTANT: Replace with your actual WiFi credentials
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// ===== MQTT Configuration =====
const char* MQTT_BROKER = "broker.hivemq.com";
const int MQTT_PORT = 1883;

// ===== MQTT Topics (Dynamic based on BOARD_ID) =====
String LED_CONTROL_TOPIC;
String LED_STATE_TOPIC;
String RELAY1_CONTROL_TOPIC;
String RELAY2_CONTROL_TOPIC;
String RELAY3_CONTROL_TOPIC;
String RELAY1_STATE_TOPIC;
String RELAY2_STATE_TOPIC;
String RELAY3_STATE_TOPIC;
String SENSOR_DATA_TOPIC;

// ===== Global Objects =====
WiFiClient espClient;
PubSubClient mqttClient(espClient);
DHT dht(DHT_PIN, DHT_TYPE);

// ===== Timing Variables =====
unsigned long lastReconnectAttempt = 0;
unsigned long lastSensorRead = 0;
unsigned long lastHeartbeat = 0;
const unsigned long SENSOR_INTERVAL = 5000;    // 5 seconds
const unsigned long HEARTBEAT_INTERVAL = 30000; // 30 seconds

// ===== Function Declarations =====
void setupTopics();
void setupWiFi();
void reconnectMQTT();
void mqttCallback(char* topic, byte* payload, unsigned int length);
void publishLedState();
void publishRelayState(int relayNum);
void readAndPublishSensorData();

// ===================================================
// SETUP FUNCTION
// ===================================================
void setup() {
  // Initialize Serial Monitor
  Serial.begin(115200);
  delay(1000);
  
  Serial.println();
  Serial.println("========================================");
  Serial.println("  ESP32 IoT Dashboard Controller v2.0");
  Serial.println("  with Board ID Support");
  Serial.println("========================================");
  Serial.print("Board ID: ");
  Serial.println(BOARD_ID);
  Serial.println();
  
  // Setup MQTT topics based on Board ID
  setupTopics();
  
  // Configure LED pin
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  Serial.println("💡 LED initialized (OFF)");
  
  // Configure Relay pins (Active Low)
  pinMode(RELAY1_PIN, OUTPUT);
  pinMode(RELAY2_PIN, OUTPUT);
  pinMode(RELAY3_PIN, OUTPUT);
  digitalWrite(RELAY1_PIN, HIGH);  // OFF (Active Low)
  digitalWrite(RELAY2_PIN, HIGH);  // OFF (Active Low)
  digitalWrite(RELAY3_PIN, HIGH);  // OFF (Active Low)
  Serial.println("🔌 Relays initialized (OFF)");
  
  // Initialize DHT sensor
  dht.begin();
  Serial.println("🌡️ DHT sensor initialized");
  
  // Connect to WiFi
  setupWiFi();
  
  // Configure MQTT
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setCallback(mqttCallback);
  
  Serial.println();
  Serial.println("✅ Setup completed!");
  Serial.println("========================================");
  Serial.println();
}

// ===================================================
// MAIN LOOP
// ===================================================
void loop() {
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("⚠️ WiFi disconnected! Reconnecting...");
    setupWiFi();
  }
  
  // Check MQTT connection
  if (!mqttClient.connected()) {
    unsigned long now = millis();
    if (now - lastReconnectAttempt > 5000) {
      lastReconnectAttempt = now;
      reconnectMQTT();
    }
  } else {
    // Process MQTT messages
    mqttClient.loop();
    
    // Read and publish sensor data periodically
    unsigned long now = millis();
    if (now - lastSensorRead >= SENSOR_INTERVAL) {
      lastSensorRead = now;
      readAndPublishSensorData();
    }
    
    // Send heartbeat periodically
    if (now - lastHeartbeat >= HEARTBEAT_INTERVAL) {
      lastHeartbeat = now;
      publishLedState();
      publishRelayState(1);
      publishRelayState(2);
      publishRelayState(3);
      Serial.println("💓 Heartbeat sent");
    }
  }
}

// ===================================================
// SETUP TOPICS
// ===================================================
void setupTopics() {
  String base = String("thaitechzone/") + BOARD_ID;
  
  LED_CONTROL_TOPIC = base + "/control/led";
  LED_STATE_TOPIC = base + "/status/led";
  
  RELAY1_CONTROL_TOPIC = base + "/control/relay1";
  RELAY2_CONTROL_TOPIC = base + "/control/relay2";
  RELAY3_CONTROL_TOPIC = base + "/control/relay3";
  
  RELAY1_STATE_TOPIC = base + "/state/relay1";
  RELAY2_STATE_TOPIC = base + "/state/relay2";
  RELAY3_STATE_TOPIC = base + "/state/relay3";
  
  SENSOR_DATA_TOPIC = base + "/sensor/data";
  
  Serial.println("📋 MQTT Topics configured:");
  Serial.println("  Control Topics:");
  Serial.println("    - " + LED_CONTROL_TOPIC);
  Serial.println("    - " + RELAY1_CONTROL_TOPIC);
  Serial.println("    - " + RELAY2_CONTROL_TOPIC);
  Serial.println("    - " + RELAY3_CONTROL_TOPIC);
  Serial.println("  State/Status Topics:");
  Serial.println("    - " + LED_STATE_TOPIC);
  Serial.println("    - " + RELAY1_STATE_TOPIC);
  Serial.println("    - " + RELAY2_STATE_TOPIC);
  Serial.println("    - " + RELAY3_STATE_TOPIC);
  Serial.println("  Sensor Topics:");
  Serial.println("    - " + SENSOR_DATA_TOPIC);
}

// ===================================================
// WIFI SETUP
// ===================================================
void setupWiFi() {
  delay(10);
  Serial.println();
  Serial.print("🔄 Connecting to WiFi: ");
  Serial.println(WIFI_SSID);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("✅ WiFi connected successfully!");
    Serial.print("📶 IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("📡 Signal Strength: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println();
    Serial.println("❌ WiFi connection failed!");
  }
}

// ===================================================
// MQTT RECONNECT
// ===================================================
void reconnectMQTT() {
  Serial.print("🔄 Connecting to MQTT Broker...");
  
  // Create unique client ID
  String clientId = String("ESP32_") + BOARD_ID + "_" + String(random(0xffff), HEX);
  
  if (mqttClient.connect(clientId.c_str())) {
    Serial.println(" Connected! ✅");
    Serial.print("📋 Client ID: ");
    Serial.println(clientId);
    
    // Subscribe to control topics
    mqttClient.subscribe(LED_CONTROL_TOPIC.c_str());
    mqttClient.subscribe(RELAY1_CONTROL_TOPIC.c_str());
    mqttClient.subscribe(RELAY2_CONTROL_TOPIC.c_str());
    mqttClient.subscribe(RELAY3_CONTROL_TOPIC.c_str());
    
    Serial.println("📥 Subscribed to all control topics");
    
    // Publish initial states
    publishLedState();
    publishRelayState(1);
    publishRelayState(2);
    publishRelayState(3);
    
  } else {
    Serial.print(" Failed ❌ Error code: ");
    Serial.println(mqttClient.state());
  }
}

// ===================================================
// MQTT CALLBACK
// ===================================================
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  // Convert payload to string
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  message.toUpperCase();
  
  Serial.print("📨 Message received [");
  Serial.print(topic);
  Serial.print("]: ");
  Serial.println(message);

  // === LED CONTROL ===
  if (String(topic) == LED_CONTROL_TOPIC) {
    if (message == "ON") {
      digitalWrite(LED_PIN, HIGH);
      Serial.println("💡 LED turned ON");
      publishLedState();
    } 
    else if (message == "OFF") {
      digitalWrite(LED_PIN, LOW);
      Serial.println("🌑 LED turned OFF");
      publishLedState();
    }
  }
  
  // === RELAY 1 CONTROL ===
  else if (String(topic) == RELAY1_CONTROL_TOPIC) {
    if (message == "ON") {
      digitalWrite(RELAY1_PIN, LOW);  // Active Low
      Serial.println("🔌 Relay 1 turned ON");
      publishRelayState(1);
    } 
    else if (message == "OFF") {
      digitalWrite(RELAY1_PIN, HIGH);  // Active Low
      Serial.println("🔌 Relay 1 turned OFF");
      publishRelayState(1);
    }
  }
  
  // === RELAY 2 CONTROL ===
  else if (String(topic) == RELAY2_CONTROL_TOPIC) {
    if (message == "ON") {
      digitalWrite(RELAY2_PIN, LOW);  // Active Low
      Serial.println("🔌 Relay 2 turned ON");
      publishRelayState(2);
    } 
    else if (message == "OFF") {
      digitalWrite(RELAY2_PIN, HIGH);  // Active Low
      Serial.println("🔌 Relay 2 turned OFF");
      publishRelayState(2);
    }
  }
  
  // === RELAY 3 CONTROL ===
  else if (String(topic) == RELAY3_CONTROL_TOPIC) {
    if (message == "ON") {
      digitalWrite(RELAY3_PIN, LOW);  // Active Low
      Serial.println("🔌 Relay 3 turned ON");
      publishRelayState(3);
    } 
    else if (message == "OFF") {
      digitalWrite(RELAY3_PIN, HIGH);  // Active Low
      Serial.println("🔌 Relay 3 turned OFF");
      publishRelayState(3);
    }
  }
}

// ===================================================
// PUBLISH LED STATE
// ===================================================
void publishLedState() {
  bool ledState = digitalRead(LED_PIN);
  String stateMessage = ledState ? "ON" : "OFF";
  
  if (mqttClient.publish(LED_STATE_TOPIC.c_str(), stateMessage.c_str(), true)) {
    Serial.print("📤 LED state published: ");
    Serial.println(stateMessage);
  }
}

// ===================================================
// PUBLISH RELAY STATE
// ===================================================
void publishRelayState(int relayNum) {
  bool relayState;
  const char* stateTopic;
  
  switch(relayNum) {
    case 1:
      relayState = digitalRead(RELAY1_PIN);
      stateTopic = RELAY1_STATE_TOPIC.c_str();
      break;
    case 2:
      relayState = digitalRead(RELAY2_PIN);
      stateTopic = RELAY2_STATE_TOPIC.c_str();
      break;
    case 3:
      relayState = digitalRead(RELAY3_PIN);
      stateTopic = RELAY3_STATE_TOPIC.c_str();
      break;
    default:
      Serial.println("❌ Invalid relay number");
      return;
  }
  
  // Active Low: LOW = ON, HIGH = OFF
  String stateMessage = relayState ? "OFF" : "ON";
  
  if (mqttClient.publish(stateTopic, stateMessage.c_str(), true)) {
    Serial.print("📤 Relay ");
    Serial.print(relayNum);
    Serial.print(" state published: ");
    Serial.println(stateMessage);
  }
}

// ===================================================
// READ AND PUBLISH SENSOR DATA
// ===================================================
void readAndPublishSensorData() {
  // Read temperature and humidity
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  
  // Check if readings are valid
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("❌ Failed to read from DHT sensor!");
    return;
  }
  
  // Create JSON document
  StaticJsonDocument<200> doc;
  doc["device"] = BOARD_ID;
  doc["temperature"] = round(temperature * 10) / 10.0;  // Round to 1 decimal
  doc["humidity"] = round(humidity * 10) / 10.0;        // Round to 1 decimal
  doc["timestamp"] = millis();
  
  // Serialize to string
  String jsonString;
  serializeJson(doc, jsonString);
  
  // Publish to MQTT
  if (mqttClient.publish(SENSOR_DATA_TOPIC.c_str(), jsonString.c_str())) {
    Serial.print("📤 Sensor data published: ");
    Serial.print("Temp=");
    Serial.print(temperature, 1);
    Serial.print("°C, Hum=");
    Serial.print(humidity, 1);
    Serial.println("%");
  } else {
    Serial.println("❌ Failed to publish sensor data");
  }
}
