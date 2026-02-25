#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ===== Device Class Headers =====
#include "DevRelay.h"        // Relay controller (Active Low/High)
#include "DevSwitch.h"       // Button with debounce, click, long-press
#include "DevIsoInput.h"     // Isolated Digital Input with debounce
#include "DevPZEM.h"         // PZEM-016 AC Power Monitor (Modbus RTU)
#include "DevTempHumidity.h" // XY-MD03 Temp/Humidity Sensor (Modbus RTU)

// ===== DS18B20 Temperature Sensor =====
#include <OneWire.h>
#include <DallasTemperature.h>

// ===== Pin Definitions =====
#define LED_PIN     2  // The onboard LED is on GPIO2 (Active High)
#define DHT_PIN     15 // DHT sensor pin (GPIO15)
#define DS18B20_PIN 14 // DS18B20 temperature sensor (GPIO14, 1-Wire)
#define DHT_TYPE DHT22 // DHT22 (AM2302)
#define RELAY1_PIN  17 // Relay 1 pin (GPIO17)
#define RELAY2_PIN  16 // Relay 2 pin (GPIO16)
#define RELAY3_PIN   4 // Relay 3 pin (GPIO4)

// Button pins
#define SW1_PIN 34 // Button 1 for Relay 1 (with External Pull-up)
#define SW2_PIN 35 // Button 2 for Relay 2 (with External Pull-up)
#define SW3_PIN 32 // Button 3 for Relay 3 (INPUT_PULLUP)

// Isolated Input pins
#define ISOLATE_IN1 33 // Isolated Input 1 (with External Pull-up, Active LOW)
#define ISOLATE_IN2 27 // Isolated Input 2 (with External Pull-up, Active LOW)

// OLED Display settings
#define SCREEN_WIDTH    128
#define SCREEN_HEIGHT    64
#define OLED_RESET       -1
#define SCREEN_ADDRESS 0x3C

// ===== WiFi Configuration =====
// IMPORTANT: Replace with your actual WiFi credentials
const char* WIFI_SSID     = "myHome_2.4GHz";
const char* WIFI_PASSWORD = "0939391546";

// ===== MQTT Configuration =====
const char* MQTT_BROKER = "broker.hivemq.com";
const int   MQTT_PORT   = 1883;

// --- Device Identity (Custom UUID - SET THIS BEFORE FLASHING EACH BOARD) ---
// !! CHANGE THIS VALUE FOR EVERY BOARD !!
// Naming convention: <project>_<location>_<number>
// Examples: "ttz_factory_001", "ttz_office_002", "ttz_warehouse_003"
#define DEVICE_NAME "ttz_board_001"

String DEVICE_ID;       // Set from DEVICE_NAME at runtime
String MQTT_CLIENT_ID;  // e.g. "ThaiTechZone_ttz_board_001"

// --- MQTT Topics (Dynamically built from DEVICE_ID) ---
// Pattern: thaitechzone/v2/<device_id>/<direction>/<property>
// This ensures NO topic collision between multiple boards
String LED_CONTROL_TOPIC;
String LED_STATE_TOPIC;
String RELAY1_CONTROL_TOPIC;
String RELAY2_CONTROL_TOPIC;
String RELAY3_CONTROL_TOPIC;
String RELAY1_STATE_TOPIC;
String RELAY2_STATE_TOPIC;
String RELAY3_STATE_TOPIC;
String TEMPERATURE_TOPIC;
String HUMIDITY_TOPIC;
String SENSOR_DATA_TOPIC;
String ISOLATE_IN1_STATE_TOPIC;
String ISOLATE_IN2_STATE_TOPIC;
String DS18B20_TOPIC;

// ===== Global Objects =====
WiFiClient espClient;
PubSubClient mqttClient(espClient);
DHT dht(DHT_PIN, DHT_TYPE);
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// DS18B20 objects
OneWire oneWire(DS18B20_PIN);
DallasTemperature ds18b20(&oneWire);

// XY-MD03 Temp/Humidity Sensor (Modbus RTU via Serial0 / UART0)
// NOTE: Serial baud rate must be 9600 to match XY-MD03 default (9600 8N1)
DevTempHumidity xyMD03(&Serial, 1); // Slave ID = 1 (default)

long last_reconnect_attempt = 0;
unsigned long lastSensorRead           = 0;
unsigned long lastDS18B20Read          = 0;
unsigned long lastDisplayUpdate        = 0;
unsigned long lastIsolatedInputPublish = 0;
const unsigned long SENSOR_INTERVAL                 = 5000; // Send sensor data every 5 seconds
const unsigned long DS18B20_INTERVAL                = 5000; // Read DS18B20 every 5 seconds
const unsigned long DISPLAY_UPDATE_INTERVAL         =  500; // Update display every 500ms
const unsigned long ISOLATED_INPUT_PUBLISH_INTERVAL = 2000; // Publish isolated input states every 2 seconds

// Store current sensor values for display
float currentTemperature = 0.0;
float currentHumidity    = 0.0;
float currentDS18B20Temp = 0.0; // DS18B20 real temperature for display

// OLED Display availability flag
bool oledAvailable = false;

// Button states
bool lastSW1State = HIGH;
bool lastSW2State = HIGH;
bool lastSW3State = HIGH;
unsigned long lastDebounceTime1    = 0;
unsigned long lastDebounceTime2    = 0;
unsigned long lastDebounceTime3    = 0;
const unsigned long debounceDelay  = 50;

// Isolated Input states
bool lastIsolateIn1State            = HIGH;
bool lastIsolateIn2State            = HIGH;
unsigned long lastIsolateIn1DebounceTime = 0;
unsigned long lastIsolateIn2DebounceTime = 0;

// ===== Function Declarations =====
void setup_wifi();
void callback(char* topic, byte* payload, unsigned int length);
void reconnectMQTT();
void publishLedState();
void publishRelayState(int relayNum);
void readAndPublishSensorData();
void readAndPublishDS18B20();
void publishSensorDataJSON(float temperature, float humidity);
void updateDisplay();
void checkButtons();
void toggleRelay(int relayNum);
void checkIsolatedInputs();
void publishIsolatedInputState(int inputNum);

void setup() {
  // NOTE: 9600 baud required — XY-MD03 Modbus RTU shares Serial0 (UART0) at 9600
  Serial.begin(9600);
  Serial.println("\n=== ESP32 MQTT LED Controller Starting ===");

  // --- Set Device ID from custom DEVICE_NAME define ---
  // To deploy a new board: change #define DEVICE_NAME above and re-flash
  DEVICE_ID     = String(DEVICE_NAME);
  MQTT_CLIENT_ID = String("ThaiTechZone_") + DEVICE_ID;

  // --- Build MQTT Topics using Device ID ---
  // Format: thaitechzone/v2/<device_id>/<direction>/<property>
  String base = String("thaitechzone/v2/") + DEVICE_ID;
  LED_CONTROL_TOPIC       = base + "/control/led";
  LED_STATE_TOPIC         = base + "/state/led";
  RELAY1_CONTROL_TOPIC    = base + "/control/relay1";
  RELAY2_CONTROL_TOPIC    = base + "/control/relay2";
  RELAY3_CONTROL_TOPIC    = base + "/control/relay3";
  RELAY1_STATE_TOPIC      = base + "/state/relay1";
  RELAY2_STATE_TOPIC      = base + "/state/relay2";
  RELAY3_STATE_TOPIC      = base + "/state/relay3";
  TEMPERATURE_TOPIC       = base + "/sensor/temperature";
  HUMIDITY_TOPIC          = base + "/sensor/humidity";
  SENSOR_DATA_TOPIC       = base + "/sensor/data";
  ISOLATE_IN1_STATE_TOPIC = base + "/state/isolate_in1";
  ISOLATE_IN2_STATE_TOPIC = base + "/state/isolate_in2";
  DS18B20_TOPIC           = base + "/sensor/ds18b20";

  Serial.print("Device ID  : "); Serial.println(DEVICE_ID);
  Serial.print("Base Topic : "); Serial.println(base);

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

  // Configure Isolated Input pins with pull-up resistors
  // Note: GPIO 33, 27 use external pull-up resistors (10kΩ to 3.3V)
  pinMode(ISOLATE_IN1, INPUT_PULLUP);
  pinMode(ISOLATE_IN2, INPUT_PULLUP);
  Serial.println("Isolated Inputs IN1, IN2 initialized");
  
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

  // Initialize XY-MD03 Temp/Humidity Sensor (Modbus RTU on Serial0)
  xyMD03.begin(9600);
  Serial.println("XY-MD03 sensor initialized (Modbus RTU, Slave ID=1, 9600 baud)");

  // Initialize DS18B20 sensor
  ds18b20.begin();
  int ds18b20Count = ds18b20.getDeviceCount();
  Serial.print("DS18B20 sensors found: ");
  Serial.println(ds18b20Count);
  if (ds18b20Count == 0) {
    Serial.println("WARNING: No DS18B20 sensor found on GPIO14");
  }
  
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

    // Check isolated input states
    checkIsolatedInputs();
    
    // Read and publish sensor data periodically
    unsigned long now = millis();
    if (now - lastSensorRead >= SENSOR_INTERVAL) {
      lastSensorRead = now;
      readAndPublishSensorData();
    }

    // Read and publish DS18B20 temperature periodically
    if (now - lastDS18B20Read >= DS18B20_INTERVAL) {
      lastDS18B20Read = now;
      readAndPublishDS18B20();
    }

    // Publish isolated input states periodically
    if (now - lastIsolatedInputPublish >= ISOLATED_INPUT_PUBLISH_INTERVAL) {
      lastIsolatedInputPublish = now;
      publishIsolatedInputState(1);
      publishIsolatedInputState(2);
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
  if (String(topic) == LED_CONTROL_TOPIC.c_str()) {
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
  else if (String(topic) == RELAY1_CONTROL_TOPIC.c_str()) {
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
  else if (String(topic) == RELAY2_CONTROL_TOPIC.c_str()) {
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
  else if (String(topic) == RELAY3_CONTROL_TOPIC.c_str()) {
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
  if (mqttClient.publish(LED_STATE_TOPIC.c_str(), stateMessage.c_str(), true)) {
    Serial.print("State published: ");
    Serial.println(stateMessage);
  } else {
    Serial.println("Failed to publish state");
  }
}

void publishRelayState(int relayNum) {
  bool relayState;
  String stateTopic;
  
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
  if (mqttClient.publish(stateTopic.c_str(), stateMessage.c_str(), true)) {
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
  
  // Append random suffix to avoid session conflicts on reconnect
  String clientId = MQTT_CLIENT_ID + "_" + String(random(0xffff), HEX);
  
  if (mqttClient.connect(clientId.c_str())) {
    Serial.println(" connected!");
    
    // Subscribe to control topics
    if (mqttClient.subscribe(LED_CONTROL_TOPIC.c_str())) {
      Serial.print("Subscribed to: "); Serial.println(LED_CONTROL_TOPIC);
    } else {
      Serial.println("Failed to subscribe to LED control topic");
    }
    
    if (mqttClient.subscribe(RELAY1_CONTROL_TOPIC.c_str())) {
      Serial.print("Subscribed to: "); Serial.println(RELAY1_CONTROL_TOPIC);
    } else {
      Serial.println("Failed to subscribe to Relay 1 control topic");
    }
    
    if (mqttClient.subscribe(RELAY2_CONTROL_TOPIC.c_str())) {
      Serial.print("Subscribed to: "); Serial.println(RELAY2_CONTROL_TOPIC);
    } else {
      Serial.println("Failed to subscribe to Relay 2 control topic");
    }
    
    if (mqttClient.subscribe(RELAY3_CONTROL_TOPIC.c_str())) {
      Serial.print("Subscribed to: "); Serial.println(RELAY3_CONTROL_TOPIC);
    } else {
      Serial.println("Failed to subscribe to Relay 3 control topic");
    }
    
    // Publish initial states
    publishLedState();
    publishRelayState(1);
    publishRelayState(2);
    publishRelayState(3);
    publishIsolatedInputState(1);
    publishIsolatedInputState(2);
    
  } else {
    Serial.print(" failed, rc=");
    Serial.print(mqttClient.state());
    Serial.println(" retrying in 5 seconds...");
  }
}

void readAndPublishSensorData() {
  // Read real values from XY-MD03 Temp/Humidity Sensor (Modbus RTU)
  bool readOK = xyMD03.update();

  float temperature = readOK ? xyMD03.getTemperature() : 0.0;
  float humidity    = readOK ? xyMD03.getHumidity()    : 0.0;

  if (readOK) {
    Serial.print("[XY-MD03] Temperature: ");
    Serial.print(temperature, 1);
    Serial.print(" °C, Humidity: ");
    Serial.print(humidity, 1);
    Serial.println(" %");
  } else {
    Serial.println("[XY-MD03] Read failed — publishing 0.0");
  }

  // Store values for display
  currentTemperature = temperature;
  currentHumidity    = humidity;

  // Publish individual topics
  String tempStr = String(temperature, 1);
  String humStr  = String(humidity, 1);

  if (mqttClient.publish(TEMPERATURE_TOPIC.c_str(), tempStr.c_str())) {
    Serial.println("Temperature published successfully");
  } else {
    Serial.println("Failed to publish temperature");
  }

  if (mqttClient.publish(HUMIDITY_TOPIC.c_str(), humStr.c_str())) {
    Serial.println("Humidity published successfully");
  } else {
    Serial.println("Failed to publish humidity");
  }

  // Also publish as JSON format
  publishSensorDataJSON(temperature, humidity);
}

void readAndPublishDS18B20() {
  // Read real DS18B20 temperature sensor (1-Wire on GPIO14)
  ds18b20.requestTemperatures();
  float temp = ds18b20.getTempCByIndex(0);

  // DEVICE_DISCONNECTED_C = -127.0 — fallback to 0.0 if not connected
  if (temp == DEVICE_DISCONNECTED_C || temp < -100.0) {
    temp = 0.0;
    Serial.println("DS18B20: Not connected or read failed — publishing 0.0");
  } else {
    Serial.print("DS18B20: ");
    Serial.print(temp, 1);
    Serial.println(" °C");
  }

  currentDS18B20Temp = temp; // Store for OLED display

  String tempStr = String(temp, 1);
  if (mqttClient.publish(DS18B20_TOPIC.c_str(), tempStr.c_str(), true)) {
    Serial.println("DS18B20 topic published");
  } else {
    Serial.println("Failed to publish DS18B20 topic");
  }
}

void publishSensorDataJSON(float temperature, float humidity) {
  // Create JSON payload in the exact format requested
  StaticJsonDocument<200> doc;
  doc["temperature"] = round(temperature * 10) / 10.0; // Round to 1 decimal place
  doc["humidity"]    = round(humidity * 10) / 10.0;    // Round to 1 decimal place
  doc["device_name"] = DEVICE_ID;                      // Use dynamic device ID
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  if (mqttClient.publish(SENSOR_DATA_TOPIC.c_str(), jsonString.c_str())) {
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
  
  // DS18B20 Temperature (replaces WiFi RSSI line)
  display.setCursor(0, 14);
  display.print(F("DS18B20:"));
  if (currentDS18B20Temp == 0.0) {
    display.print(F("--.-"));
  } else {
    display.print(currentDS18B20Temp, 1);
  }
  display.print(F("C "));
  // WiFi status indicator (compact)
  display.print(WiFi.status() == WL_CONNECTED ? F("W:OK") : F("W:--"));
  display.println();
  
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
  
  // LED Status and Isolated Inputs
  display.setCursor(0, 56);
  display.print(F("LED:"));
  display.print(digitalRead(LED_PIN) ? F("ON ") : F("OFF"));

  display.print(F(" I1:"));
  bool in1Active = (digitalRead(ISOLATE_IN1) == LOW); // Active LOW
  display.print(in1Active ? F("ON ") : F("OFF"));

  display.print(F(" I2:"));
  bool in2Active = (digitalRead(ISOLATE_IN2) == LOW); // Active LOW
  display.print(in2Active ? F("ON") : F("OFF"));

  display.display();
}

void checkIsolatedInputs() {
  unsigned long currentTime = millis();

  // Check ISOLATE_IN1
  bool in1Reading = digitalRead(ISOLATE_IN1);
  if (in1Reading != lastIsolateIn1State) {
    lastIsolateIn1DebounceTime = currentTime;
  }
  if ((currentTime - lastIsolateIn1DebounceTime) > debounceDelay) {
    if (in1Reading != lastIsolateIn1State) {
      lastIsolateIn1State = in1Reading;
      Serial.print("Isolated Input 1 state changed: ");
      Serial.println(in1Reading == LOW ? "ACTIVE (ON)" : "INACTIVE (OFF)");
      publishIsolatedInputState(1);
    }
  }

  // Check ISOLATE_IN2
  bool in2Reading = digitalRead(ISOLATE_IN2);
  if (in2Reading != lastIsolateIn2State) {
    lastIsolateIn2DebounceTime = currentTime;
  }
  if ((currentTime - lastIsolateIn2DebounceTime) > debounceDelay) {
    if (in2Reading != lastIsolateIn2State) {
      lastIsolateIn2State = in2Reading;
      Serial.print("Isolated Input 2 state changed: ");
      Serial.println(in2Reading == LOW ? "ACTIVE (ON)" : "INACTIVE (OFF)");
      publishIsolatedInputState(2);
    }
  }
}

void publishIsolatedInputState(int inputNum) {
  bool inputState;
  String stateTopic;

  switch (inputNum) {
    case 1:
      inputState = digitalRead(ISOLATE_IN1);
      stateTopic = ISOLATE_IN1_STATE_TOPIC;
      break;
    case 2:
      inputState = digitalRead(ISOLATE_IN2);
      stateTopic = ISOLATE_IN2_STATE_TOPIC;
      break;
    default:
      Serial.println("Invalid isolated input number");
      return;
  }

  // Active LOW: LOW = ON, HIGH = OFF
  String stateMessage = inputState == LOW ? "ON" : "OFF";

  if (mqttClient.publish(stateTopic.c_str(), stateMessage.c_str(), true)) {
    Serial.print("Isolated Input ");
    Serial.print(inputNum);
    Serial.print(" state published: ");
    Serial.println(stateMessage);
  } else {
    Serial.print("Failed to publish Isolated Input ");
    Serial.print(inputNum);
    Serial.println(" state");
  }
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