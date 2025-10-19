#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// ===== Pin Definitions =====
#define LED_PIN 2 // The onboard LED is on GPIO2 (Active High)
#define DHT_PIN 15 // DHT sensor pin (GPIO4)
#define DHT_TYPE DHT22 // DHT22 (AM2302)
#define RELAY1_PIN 17 // Relay 1 pin (GPIO12)
#define RELAY2_PIN 16 // Relay 2 pin (GPIO13)
#define RELAY3_PIN 4 // Relay 3 pin (GPIO14)

// ===== WiFi Configuration =====
// IMPORTANT: Replace with your actual WiFi credentials
const char* WIFI_SSID = "myHome_2.4GHz";
const char* WIFI_PASSWORD = "0939391546";

// ===== MQTT Configuration =====
const char* MQTT_BROKER = "broker.hivemq.com";
const int MQTT_PORT = 1883;
const char* MQTT_CLIENT_ID = "ESP_ThaiTechZone_LED_Controller_01"; // A unique name

// --- MQTT Topics (Matching the Django Dashboard) ---
// Topic this ESP32 LISTENS to for commands
const char* LED_CONTROL_TOPIC = "thaitechzone/v2_board/control/led";
// Topic this ESP32 PUBLISHES its status to
const char* LED_STATE_TOPIC = "thaitechzone/v2_board/state/led";
// Relay control topics
const char* RELAY1_CONTROL_TOPIC = "thaitechzone/v2_board/control/relay1";
const char* RELAY2_CONTROL_TOPIC = "thaitechzone/v2_board/control/relay2";
const char* RELAY3_CONTROL_TOPIC = "thaitechzone/v2_board/control/relay3";
// Relay state topics
const char* RELAY1_STATE_TOPIC = "thaitechzone/v2_board/state/relay1";
const char* RELAY2_STATE_TOPIC = "thaitechzone/v2_board/state/relay2";
const char* RELAY3_STATE_TOPIC = "thaitechzone/v2_board/state/relay3";
// Topics for sensor data
const char* TEMPERATURE_TOPIC = "thaitechzone/v2_board/sensor/temperature";
const char* HUMIDITY_TOPIC = "thaitechzone/v2_board/sensor/humidity";
const char* SENSOR_DATA_TOPIC = "thaitechzone/v2_board/sensors/data";

// ===== Global Objects =====
WiFiClient espClient;
PubSubClient mqttClient(espClient);
DHT dht(DHT_PIN, DHT_TYPE);
long last_reconnect_attempt = 0;
unsigned long lastSensorRead = 0;
const unsigned long SENSOR_INTERVAL = 5000; // Send sensor data every 5 seconds

// ===== Function Declarations =====
void setup_wifi();
void callback(char* topic, byte* payload, unsigned int length);
void reconnectMQTT();
void publishLedState();
void publishRelayState(int relayNum);
void readAndPublishSensorData();
void publishSensorDataJSON(float temperature, float humidity);

void setup() {
  // Initialize Serial Monitor
  Serial.begin(115200);
  Serial.println("\n=== ESP32 MQTT LED Controller Starting ===");
  
  // Configure LED pin
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW); // Start with LED OFF
  Serial.println("LED initialized (OFF)");
  
  // Configure Relay pins
  pinMode(RELAY1_PIN, OUTPUT);
  pinMode(RELAY2_PIN, OUTPUT);
  pinMode(RELAY3_PIN, OUTPUT);
  digitalWrite(RELAY1_PIN, HIGH); // Start with Relay 1 OFF (Active Low)
  digitalWrite(RELAY2_PIN, HIGH); // Start with Relay 2 OFF (Active Low)
  digitalWrite(RELAY3_PIN, HIGH); // Start with Relay 3 OFF (Active Low)
  Serial.println("Relay 1, 2, 3 initialized (OFF)");
  
  // Initialize DHT sensor
  dht.begin();
  Serial.println("DHT sensor initialized");
  
  // Connect to WiFi
  setup_wifi();
  
  // Configure MQTT client
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setCallback(callback);
  
  Serial.println("Setup completed!");
}

void loop() {
  // Check MQTT connection
  if (!mqttClient.connected()) {
    long now = millis();
    if (now - last_reconnect_attempt > 5000) {
      last_reconnect_attempt = now;
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
  }
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi connected successfully!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.print("Signal strength (RSSI): ");
  Serial.print(WiFi.RSSI());
  Serial.println(" dBm");
}

void callback(char* topic, byte* payload, unsigned int length) {
  // Convert payload to string
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  message.toUpperCase(); // Convert to uppercase for consistency
  
  Serial.print("Message received [");
  Serial.print(topic);
  Serial.print("]: ");
  Serial.println(message);

  // Check if message is for LED control
  if (String(topic) == LED_CONTROL_TOPIC) {
    if (message == "ON") {
      digitalWrite(LED_PIN, HIGH);
      Serial.println("LED turned ON");
    } else if (message == "OFF") {
      digitalWrite(LED_PIN, LOW);
      Serial.println("LED turned OFF");
    } else {
      Serial.println("Unknown command: " + message);
      return; // Don't publish state for unknown commands
    }
    
    // Always publish state after changing LED
    publishLedState();
  }
  // Check if message is for Relay 1 control
  else if (String(topic) == RELAY1_CONTROL_TOPIC) {
    if (message == "ON") {
      digitalWrite(RELAY1_PIN, LOW); // Active Low: LOW = ON
      Serial.println("Relay 1 turned ON");
    } else if (message == "OFF") {
      digitalWrite(RELAY1_PIN, HIGH); // Active Low: HIGH = OFF
      Serial.println("Relay 1 turned OFF");
    } else {
      Serial.println("Unknown command: " + message);
      return;
    }
    publishRelayState(1);
  }
  // Check if message is for Relay 2 control
  else if (String(topic) == RELAY2_CONTROL_TOPIC) {
    if (message == "ON") {
      digitalWrite(RELAY2_PIN, LOW); // Active Low: LOW = ON
      Serial.println("Relay 2 turned ON");
    } else if (message == "OFF") {
      digitalWrite(RELAY2_PIN, HIGH); // Active Low: HIGH = OFF
      Serial.println("Relay 2 turned OFF");
    } else {
      Serial.println("Unknown command: " + message);
      return;
    }
    publishRelayState(2);
  }
  // Check if message is for Relay 3 control
  else if (String(topic) == RELAY3_CONTROL_TOPIC) {
    if (message == "ON") {
      digitalWrite(RELAY3_PIN, LOW); // Active Low: LOW = ON
      Serial.println("Relay 3 turned ON");
    } else if (message == "OFF") {
      digitalWrite(RELAY3_PIN, HIGH); // Active Low: HIGH = OFF
      Serial.println("Relay 3 turned OFF");
    } else {
      Serial.println("Unknown command: " + message);
      return;
    }
    publishRelayState(3);
  }
}

void publishLedState() {
  // Read current LED state
  bool ledState = digitalRead(LED_PIN);
  String stateMessage = ledState ? "ON" : "OFF";
  
  // Publish with retain flag
  if (mqttClient.publish(LED_STATE_TOPIC, stateMessage.c_str(), true)) {
    Serial.print("State published: ");
    Serial.println(stateMessage);
  } else {
    Serial.println("Failed to publish state");
  }
}

void publishRelayState(int relayNum) {
  bool relayState;
  const char* stateTopic;
  
  // Get relay state and topic based on relay number
  switch(relayNum) {
    case 1:
      relayState = digitalRead(RELAY1_PIN);
      stateTopic = RELAY1_STATE_TOPIC;
      break;
    case 2:
      relayState = digitalRead(RELAY2_PIN);
      stateTopic = RELAY2_STATE_TOPIC;
      break;
    case 3:
      relayState = digitalRead(RELAY3_PIN);
      stateTopic = RELAY3_STATE_TOPIC;
      break;
    default:
      Serial.println("Invalid relay number");
      return;
  }
  
  // Active Low: LOW = ON, HIGH = OFF
  String stateMessage = relayState ? "OFF" : "ON";
  
  // Publish with retain flag
  if (mqttClient.publish(stateTopic, stateMessage.c_str(), true)) {
    Serial.print("Relay ");
    Serial.print(relayNum);
    Serial.print(" state published: ");
    Serial.println(stateMessage);
  } else {
    Serial.print("Failed to publish Relay ");
    Serial.print(relayNum);
    Serial.println(" state");
  }
}

void reconnectMQTT() {
  Serial.print("Attempting MQTT connection...");
  
  // Create a random client ID to avoid conflicts
  String clientId = MQTT_CLIENT_ID;
  clientId += String(random(0xffff), HEX);
  
  if (mqttClient.connect(clientId.c_str())) {
    Serial.println(" connected!");
    
    // Subscribe to control topics
    if (mqttClient.subscribe(LED_CONTROL_TOPIC)) {
      Serial.print("Subscribed to: ");
      Serial.println(LED_CONTROL_TOPIC);
    } else {
      Serial.println("Failed to subscribe to LED control topic");
    }
    
    if (mqttClient.subscribe(RELAY1_CONTROL_TOPIC)) {
      Serial.print("Subscribed to: ");
      Serial.println(RELAY1_CONTROL_TOPIC);
    } else {
      Serial.println("Failed to subscribe to Relay 1 control topic");
    }
    
    if (mqttClient.subscribe(RELAY2_CONTROL_TOPIC)) {
      Serial.print("Subscribed to: ");
      Serial.println(RELAY2_CONTROL_TOPIC);
    } else {
      Serial.println("Failed to subscribe to Relay 2 control topic");
    }
    
    if (mqttClient.subscribe(RELAY3_CONTROL_TOPIC)) {
      Serial.print("Subscribed to: ");
      Serial.println(RELAY3_CONTROL_TOPIC);
    } else {
      Serial.println("Failed to subscribe to Relay 3 control topic");
    }
    
    // Publish initial states
    publishLedState();
    publishRelayState(1);
    publishRelayState(2);
    publishRelayState(3);
    
  } else {
    Serial.print(" failed, rc=");
    Serial.print(mqttClient.state());
    Serial.println(" retrying in 5 seconds...");
  }
}

void readAndPublishSensorData() {
  // For now, generate random values
  // Later you can replace this with actual DHT sensor readings
  float temperature = random(200, 350) / 10.0; // Random temp between 20.0-35.0°C
  float humidity = random(400, 800) / 10.0;    // Random humidity between 40.0-80.0%
  
  // Uncomment these lines when you have a real DHT sensor connected
  /*
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  
  // Check if any reads failed and return early (to try again)
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }
  */
  
  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.print("°C, Humidity: ");
  Serial.print(humidity);
  Serial.println("%");
  
  // Publish individual topics
  String tempStr = String(temperature, 1);
  String humStr = String(humidity, 1);
  
  if (mqttClient.publish(TEMPERATURE_TOPIC, tempStr.c_str())) {
    Serial.println("Temperature published successfully");
  } else {
    Serial.println("Failed to publish temperature");
  }
  
  if (mqttClient.publish(HUMIDITY_TOPIC, humStr.c_str())) {
    Serial.println("Humidity published successfully");
  } else {
    Serial.println("Failed to publish humidity");
  }
  
  // Also publish as JSON format
  publishSensorDataJSON(temperature, humidity);
}

void publishSensorDataJSON(float temperature, float humidity) {
  // Create JSON payload in the exact format requested
  StaticJsonDocument<200> doc;
  doc["temperature"] = round(temperature * 10) / 10.0; // Round to 1 decimal place
  doc["humidity"] = round(humidity * 10) / 10.0;       // Round to 1 decimal place
  doc["device_name"] = "ESP_01";
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  if (mqttClient.publish(SENSOR_DATA_TOPIC, jsonString.c_str())) {
    Serial.print("Sensor data JSON published: ");
    Serial.println(jsonString);
  } else {
    Serial.println("Failed to publish sensor data JSON");
  }
}