#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ===== Pin Definitions =====
#define LED_PIN 2 // The onboard LED is on GPIO2 (Active High)
#define DHT_PIN 15 // DHT sensor pin (GPIO15)
#define DHT_TYPE DHT22 // DHT22 (AM2302)
#define RELAY1_PIN 17 // Relay 1 pin (GPIO17)
#define RELAY2_PIN 16 // Relay 2 pin (GPIO16)
#define RELAY3_PIN 4 // Relay 3 pin (GPIO4)

// Button pins
#define SW1_PIN 34 // Button 1 for Relay 1 (with External Pull-up)
#define SW2_PIN 35 // Button 2 for Relay 2 (with External Pull-up)
#define SW3_PIN 32 // Button 3 for Relay 3 (INPUT_PULLUP)

// OLED Display settings
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define SCREEN_ADDRESS 0x3C

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
const char* LED_CONTROL_TOPIC = "thaitechzone/v2_board1/control/led";
// Topic this ESP32 PUBLISHES its status to
const char* LED_STATE_TOPIC = "thaitechzone/v2_board1/state/led";
// Relay control topics
const char* RELAY1_CONTROL_TOPIC = "thaitechzone/v2_board1/control/relay1";
const char* RELAY2_CONTROL_TOPIC = "thaitechzone/v2_board1/control/relay2";
const char* RELAY3_CONTROL_TOPIC = "thaitechzone/v2_board1/control/relay3";
// Relay state topics
const char* RELAY1_STATE_TOPIC = "thaitechzone/v2_board1/state/relay1";
const char* RELAY2_STATE_TOPIC = "thaitechzone/v2_board1/state/relay2";
const char* RELAY3_STATE_TOPIC = "thaitechzone/v2_board1/state/relay3";
// Topics for sensor data
const char* TEMPERATURE_TOPIC = "thaitechzone/v2_board1/sensor/temperature";
const char* HUMIDITY_TOPIC = "thaitechzone/v2_board1/sensor/humidity";
const char* SENSOR_DATA_TOPIC = "thaitechzone/v2_board1/sensor/data";

// ===== Global Objects =====
WiFiClient espClient;
PubSubClient mqttClient(espClient);
DHT dht(DHT_PIN, DHT_TYPE);
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

long last_reconnect_attempt = 0;
unsigned long lastSensorRead = 0;
unsigned long lastDisplayUpdate = 0;
const unsigned long SENSOR_INTERVAL = 5000; // Send sensor data every 5 seconds
const unsigned long DISPLAY_UPDATE_INTERVAL = 500; // Update display every 500ms

// Store current sensor values for display
float currentTemperature = 0.0;
float currentHumidity = 0.0;

// OLED Display availability flag
bool oledAvailable = false;

// Button states
bool lastSW1State = HIGH;
bool lastSW2State = HIGH;
bool lastSW3State = HIGH;
unsigned long lastDebounceTime1 = 0;
unsigned long lastDebounceTime2 = 0;
unsigned long lastDebounceTime3 = 0;
const unsigned long debounceDelay = 50;

// ===== Function Declarations =====
void setup_wifi();
void callback(char* topic, byte* payload, unsigned int length);
void reconnectMQTT();
void publishLedState();
void publishRelayState(int relayNum);
void readAndPublishSensorData();
void publishSensorDataJSON(float temperature, float humidity);
void updateDisplay();
void checkButtons();
void toggleRelay(int relayNum);

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
  
  // Configure Button pins with pull-up resistors
  // Note: GPIO 34, 35 use external pull-up resistors (10kΩ to 3.3V)
  // GPIO 32 uses internal pull-up resistor
  pinMode(SW1_PIN, INPUT_PULLUP);
  pinMode(SW2_PIN, INPUT_PULLUP);
  pinMode(SW3_PIN, INPUT_PULLUP);
  Serial.println("Buttons SW1, SW2, SW3 initialized");
  
  // Initialize OLED Display
  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed or not connected"));
    Serial.println(F("Continuing without OLED display..."));
    oledAvailable = false;
  } else {
    oledAvailable = true;
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0, 0);
    display.println(F("ESP32 IoT System"));
    display.println(F("Initializing..."));
    display.display();
    Serial.println("OLED Display initialized");
    delay(2000);
  }
  
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
    
    // Check button states
    checkButtons();
    
    // Read and publish sensor data periodically
    unsigned long now = millis();
    if (now - lastSensorRead >= SENSOR_INTERVAL) {
      lastSensorRead = now;
      readAndPublishSensorData();
    }
    
    // Update OLED display periodically
    if (now - lastDisplayUpdate >= DISPLAY_UPDATE_INTERVAL) {
      lastDisplayUpdate = now;
      updateDisplay();
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
  
  // Store values for display
  currentTemperature = temperature;
  currentHumidity = humidity;
  
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

void updateDisplay() {
  // Skip if OLED is not available
  if (!oledAvailable) {
    return;
  }
  
  display.clearDisplay();
  
  // Header
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println(F("ESP32 IoT Control"));
  display.drawLine(0, 10, 128, 10, SSD1306_WHITE);
  
  // WiFi Status
  display.setCursor(0, 14);
  if (WiFi.status() == WL_CONNECTED) {
    display.print(F("WiFi: OK "));
    display.print(WiFi.RSSI());
    display.println(F("dBm"));
  } else {
    display.println(F("WiFi: Disconnected"));
  }
  
  // MQTT Status
  display.setCursor(0, 24);
  if (mqttClient.connected()) {
    display.println(F("MQTT: Connected"));
  } else {
    display.println(F("MQTT: Disconnected"));
  }
  
  display.drawLine(0, 34, 128, 34, SSD1306_WHITE);
  
  // Relay Status
  display.setTextSize(1);
  display.setCursor(0, 38);
  display.print(F("R1:"));
  bool relay1On = (digitalRead(RELAY1_PIN) == LOW); // Active Low
  display.print(relay1On ? F("ON ") : F("OFF"));
  
  display.print(F(" R2:"));
  bool relay2On = (digitalRead(RELAY2_PIN) == LOW); // Active Low
  display.print(relay2On ? F("ON ") : F("OFF"));
  
  display.print(F(" R3:"));
  bool relay3On = (digitalRead(RELAY3_PIN) == LOW); // Active Low
  display.println(relay3On ? F("ON ") : F("OFF"));
  
  // Temperature & Humidity
  display.setCursor(0, 48);
  display.print(F("T:"));
  display.print(currentTemperature, 1);
  display.print(F(" H:"));
  display.print(currentHumidity, 1);
  display.println(F("%"));
  
  // LED Status
  display.setCursor(0, 56);
  display.print(F("LED: "));
  display.println(digitalRead(LED_PIN) ? F("ON") : F("OFF"));
  
  display.display();
}

void checkButtons() {
  unsigned long currentTime = millis();
  
  // Check SW1
  bool sw1Reading = digitalRead(SW1_PIN);
  if (sw1Reading != lastSW1State) {
    lastDebounceTime1 = currentTime;
  }
  if ((currentTime - lastDebounceTime1) > debounceDelay) {
    if (sw1Reading == LOW) { // Button pressed (active low)
      toggleRelay(1);
      while(digitalRead(SW1_PIN) == LOW) { delay(10); } // Wait for release
    }
  }
  lastSW1State = sw1Reading;
  
  // Check SW2
  bool sw2Reading = digitalRead(SW2_PIN);
  if (sw2Reading != lastSW2State) {
    lastDebounceTime2 = currentTime;
  }
  if ((currentTime - lastDebounceTime2) > debounceDelay) {
    if (sw2Reading == LOW) { // Button pressed (active low)
      toggleRelay(2);
      while(digitalRead(SW2_PIN) == LOW) { delay(10); } // Wait for release
    }
  }
  lastSW2State = sw2Reading;
  
  // Check SW3
  bool sw3Reading = digitalRead(SW3_PIN);
  if (sw3Reading != lastSW3State) {
    lastDebounceTime3 = currentTime;
  }
  if ((currentTime - lastDebounceTime3) > debounceDelay) {
    if (sw3Reading == LOW) { // Button pressed (active low)
      toggleRelay(3);
      while(digitalRead(SW3_PIN) == LOW) { delay(10); } // Wait for release
    }
  }
  lastSW3State = sw3Reading;
}

void toggleRelay(int relayNum) {
  bool currentState;
  int pin;
  
  switch(relayNum) {
    case 1:
      pin = RELAY1_PIN;
      break;
    case 2:
      pin = RELAY2_PIN;
      break;
    case 3:
      pin = RELAY3_PIN;
      break;
    default:
      return;
  }
  
  currentState = digitalRead(pin);
  digitalWrite(pin, !currentState); // Toggle
  
  Serial.print("Button SW");
  Serial.print(relayNum);
  Serial.print(" pressed - Relay ");
  Serial.print(relayNum);
  Serial.println(currentState == HIGH ? " turned ON" : " turned OFF");
  
  // Publish state to MQTT
  publishRelayState(relayNum);
  
  // Update display immediately
  updateDisplay();
}