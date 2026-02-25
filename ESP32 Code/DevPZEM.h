#ifndef DEVPZEM_H
#define DEVPZEM_H

#include <Arduino.h>
#include <ModbusMaster.h>

/**
 * @file DevPZEM.h
 * @brief PZEM-016 AC Power Monitor wrapper class for ESP32 using ModbusMaster
 * @note Uses MAX13487 for RS232 to RS485 conversion (Auto Direction)
 *
 * PZEM-016 Specifications:
 * - Voltage: 80-260V AC
 * - Current: 0-100A (with external CT)
 * - Power: 0-23kW
 * - Communication: Modbus RTU (9600 8N1)
 * - Slave Address: 0x01 (default)
 *
 * Modbus Register Map:
 * - 0x0000: Voltage (V)       scale: 0.1
 * - 0x0001: Current (A)       scale: 0.001  (32-bit)
 * - 0x0003: Power (W)         scale: 0.1    (32-bit)
 * - 0x0005: Energy (Wh)       scale: 1      (32-bit)
 * - 0x0007: Frequency (Hz)    scale: 0.1
 * - 0x0008: Power Factor      scale: 0.01
 * - 0x0009: Alarm Status
 */

// Callback functions for ModbusMaster (MAX13487 auto direction)
void preTransmission() {
  Serial.flush();
}

void postTransmission() {
  delayMicroseconds(100);
}

class DevPZEM {
private:
  ModbusMaster node;
  HardwareSerial* serial;
  uint8_t slaveAddress;
  bool initialized;
  bool dataValid;
  unsigned long lastReadTime;
  const unsigned long readInterval = 2000;

  float voltage;
  float current;
  float power;
  float energy;
  float frequency;
  float powerFactor;
  uint16_t alarmStatus;

  uint32_t read32BitValue(uint16_t startReg) {
    uint8_t result = node.readInputRegisters(startReg, 2);
    if (result == node.ku8MBSuccess) {
      return node.getResponseBuffer(0) | ((uint32_t)node.getResponseBuffer(1) << 16);
    }
    return 0;
  }

public:
  DevPZEM(HardwareSerial* serial = &Serial, uint8_t addr = 0x01) {
    this->serial   = serial;
    slaveAddress   = addr;
    initialized    = false;
    dataValid      = false;
    lastReadTime   = 0;
    voltage        = 0.0;
    current        = 0.0;
    power          = 0.0;
    energy         = 0.0;
    frequency      = 0.0;
    powerFactor    = 0.0;
    alarmStatus    = 0;
  }

  bool begin() {
    while (serial->available()) { serial->read(); }
    node.begin(slaveAddress, *serial);
    node.preTransmission(preTransmission);
    node.postTransmission(postTransmission);
    delay(200);

    for (int attempt = 0; attempt < 3; attempt++) {
      uint8_t result = node.readInputRegisters(0x0000, 1);
      if (result == node.ku8MBSuccess) {
        uint16_t rawVoltage = node.getResponseBuffer(0);
        if (rawVoltage > 0 && rawVoltage < 3000) {
          initialized = true;
          dataValid   = false;
          Serial.printf("PZEM-016: Initialized successfully (Raw V=%d)\n", rawVoltage);
          return true;
        }
      }
      Serial.printf("  Attempt %d failed (0x%02X), retrying...\n", attempt + 1, result);
      delay(100);
    }

    initialized = false;
    dataValid   = false;
    Serial.println("PZEM-016: No response from sensor after 3 attempts");
    return false;
  }

  bool update() {
    if (!initialized) return false;
    unsigned long currentTime = millis();
    if (currentTime - lastReadTime < readInterval) return dataValid;
    lastReadTime = currentTime;

    while (serial->available()) { serial->read(); }

    bool readSuccess = true;

    uint8_t result = node.readInputRegisters(0x0000, 1);
    if (result == node.ku8MBSuccess) {
      voltage = node.getResponseBuffer(0) * 0.1;
    } else {
      readSuccess = false;
    }
    delay(100);

    uint32_t rawCurrent = read32BitValue(0x0001);
    current = rawCurrent * 0.001;
    delay(100);

    uint32_t rawPower = read32BitValue(0x0003);
    power = rawPower * 0.1;
    delay(100);

    uint32_t rawEnergy = read32BitValue(0x0005);
    energy = rawEnergy;
    delay(100);

    result = node.readInputRegisters(0x0007, 1);
    if (result == node.ku8MBSuccess) frequency = node.getResponseBuffer(0) * 0.1;
    delay(100);

    result = node.readInputRegisters(0x0008, 1);
    if (result == node.ku8MBSuccess) powerFactor = node.getResponseBuffer(0) * 0.01;
    delay(100);

    result = node.readInputRegisters(0x0009, 1);
    if (result == node.ku8MBSuccess) alarmStatus = node.getResponseBuffer(0);

    if (!readSuccess || voltage < 0 || voltage > 300) {
      dataValid = false;
      return false;
    }

    dataValid = true;
    return true;
  }

  bool resetEnergy() {
    if (!initialized) return false;
    uint8_t result = node.writeSingleRegister(0x0042, 0x0000);
    if (result == node.ku8MBSuccess) {
      energy = 0.0;
      return true;
    }
    return false;
  }

  bool isInitialized()  const { return initialized; }
  bool isDataValid()    const { return dataValid; }
  uint8_t getSlaveAddress() const { return slaveAddress; }
  float getVoltage()    const { return dataValid ? voltage     : 0.0; }
  float getCurrent()    const { return dataValid ? current     : 0.0; }
  float getPower()      const { return dataValid ? power       : 0.0; }
  float getEnergy()     const { return dataValid ? (energy / 1000.0) : 0.0; }
  float getFrequency()  const { return dataValid ? frequency   : 0.0; }
  float getPowerFactor() const { return dataValid ? powerFactor : 0.0; }
  uint16_t getAlarmStatus() const { return dataValid ? alarmStatus : 0; }

  void printData() const {
    if (!dataValid) { Serial.println("PZEM: No valid data"); return; }
    Serial.println("========== PZEM-016 Data ==========");
    Serial.printf("Voltage:      %.2f V\n", voltage);
    Serial.printf("Current:      %.3f A\n", current);
    Serial.printf("Power:        %.2f W\n", power);
    Serial.printf("Energy:       %.3f kWh\n", getEnergy());
    Serial.printf("Frequency:    %.1f Hz\n", frequency);
    Serial.printf("Power Factor: %.2f\n", powerFactor);
    Serial.printf("Alarm Status: 0x%04X\n", alarmStatus);
    Serial.println("===================================");
  }

  String toJSON() const {
    String json = "{";
    json += "\"slaveId\":"    + String(slaveAddress)      + ",";
    json += "\"voltage\":"    + String(voltage, 2)        + ",";
    json += "\"current\":"    + String(current, 3)        + ",";
    json += "\"power\":"      + String(power, 2)          + ",";
    json += "\"energy\":"     + String(getEnergy(), 3)    + ",";
    json += "\"frequency\":"  + String(frequency, 1)      + ",";
    json += "\"powerFactor\":" + String(powerFactor, 2)   + ",";
    json += "\"alarmStatus\":" + String(alarmStatus)       + ",";
    json += "\"valid\":"      + String(dataValid ? "true" : "false");
    json += "}";
    return json;
  }
};

#endif // DEVPZEM_H
