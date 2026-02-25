#ifndef DEV_TEMP_HUMIDITY_H
#define DEV_TEMP_HUMIDITY_H

#include <Arduino.h>
#include <ModbusMaster.h>

/**
 * @class DevTempHumidity
 * @brief คลาสสำหรับจัดการเซนเซอร์อุณหภูมิและความชื้น XY-MD03 ผ่าน Modbus RTU
 * @details รองรับการอ่านค่าอุณหภูมิและความชื้นจาก XY-MD03 Sensor
 *          รองรับ Auto Direction RS485 (ไม่ต้องใช้ DE/RE pin)
 * 
 * Default Settings:
 * - Slave ID: 1 (0x01)
 * - Baud Rate: 9600
 * - Data bits: 8, Stop bit: 1, Parity: None
 * 
 * Modbus Registers:
 * - Temperature: Register 0x0001 (หารด้วย 10)
 * - Humidity: Register 0x0002 (หารด้วย 10)
 * - Function Code: 04 (Read Input Register)
 */
class DevTempHumidity {
private:
  ModbusMaster modbus;           // Modbus Master object
  uint8_t slaveID;               // Modbus Slave ID
  HardwareSerial* serial;        // Serial port สำหรับ Modbus
  
  float temperature;             // ค่าอุณหภูมิล่าสุด (°C)
  float humidity;                // ค่าความชื้นล่าสุด (%)
  bool lastReadSuccess;          // สถานะการอ่านค่าครั้งล่าสุด
  unsigned long lastReadTime;    // เวลาที่อ่านค่าครั้งล่าสุด
  
  // Modbus Register Addresses
  static const uint16_t REG_TEMPERATURE = 0x0001;
  static const uint16_t REG_HUMIDITY    = 0x0002;

public:
  /**
   * @brief Constructor
   * @param hwSerial ตัวชี้ไปที่ HardwareSerial object (เช่น &Serial)
   * @param slaveId Modbus Slave ID (default: 1)
   */
  DevTempHumidity(HardwareSerial* hwSerial, uint8_t slaveId = 1) {
    serial          = hwSerial;
    slaveID         = slaveId;
    temperature     = 0.0;
    humidity        = 0.0;
    lastReadSuccess = false;
    lastReadTime    = 0;
  }

  /**
   * @brief เริ่มต้นการทำงาน (ใช้กับ Auto Direction RS485)
   * @param baudRate ความเร็ว Baud Rate (default: 9600)
   */
  void begin(unsigned long baudRate = 9600) {
    // เริ่มต้น Serial (สำหรับ auto direction ไม่ต้องตั้งค่า DE/RE)
    serial->begin(baudRate, SERIAL_8N1);
    
    // เริ่มต้น Modbus
    modbus.begin(slaveID, *serial);
    
    Serial.printf("[DevTempHumidity] Initialized: SlaveID=%d, Baud=%lu (Auto Direction)\n",
                  slaveID, baudRate);
  }

  /**
   * @brief อ่านค่าอุณหภูมิและความชื้นจากเซนเซอร์
   * @return true ถ้าอ่านสำเร็จ, false ถ้าอ่านไม่สำเร็จ
   */
  bool update() {
    uint8_t result;
    uint16_t data[2];
    
    // อ่านค่า 2 Registers (Temperature & Humidity) โดยใช้ Function Code 04
    result = modbus.readInputRegisters(REG_TEMPERATURE, 2);
    
    if (result == modbus.ku8MBSuccess) {
      // อ่านค่าสำเร็จ
      data[0] = modbus.getResponseBuffer(0);  // Temperature
      data[1] = modbus.getResponseBuffer(1);  // Humidity
      
      // แปลงค่า (หารด้วย 10)
      temperature = data[0] / 10.0;
      humidity    = data[1] / 10.0;
      
      lastReadSuccess = true;
      lastReadTime    = millis();
      return true;
    } else {
      // อ่านค่าไม่สำเร็จ
      lastReadSuccess = false;
      Serial.printf("[DevTempHumidity] Read failed! Error code: 0x%02X\n", result);
      return false;
    }
  }

  /** @brief ดึงค่าอุณหภูมิล่าสุด @return ค่าอุณหภูมิในหน่วย °C */
  float getTemperature() const { return temperature; }

  /** @brief ดึงค่าความชื้นล่าสุด @return ค่าความชื้นในหน่วย % */
  float getHumidity() const { return humidity; }

  /** @brief ตรวจสอบว่าการอ่านค่าครั้งล่าสุดสำเร็จหรือไม่ */
  bool isLastReadSuccess() const { return lastReadSuccess; }

  /** @brief ดึงเวลาที่อ่านค่าครั้งล่าสุด @return เวลาใน milliseconds */
  unsigned long getLastReadTime() const { return lastReadTime; }

  /** @brief แสดงข้อมูลทั้งหมดทาง Serial */
  void printInfo() const {
    Serial.println("=== XY-MD03 Temperature & Humidity Sensor ===");
    Serial.printf("Temperature: %.1f °C\n", temperature);
    Serial.printf("Humidity: %.1f %%\n", humidity);
    Serial.printf("Last Read: %s (%lu ms ago)\n",
                  lastReadSuccess ? "Success" : "Failed",
                  millis() - lastReadTime);
    Serial.println("=============================================");
  }

  /** @brief เปลี่ยน Slave ID */
  void setSlaveID(uint8_t newSlaveId) {
    slaveID = newSlaveId;
    modbus.begin(slaveID, *serial);
    Serial.printf("[DevTempHumidity] Slave ID changed to: %d\n", slaveID);
  }

  /** @brief ดึง Slave ID ปัจจุบัน */
  uint8_t getSlaveID() const { return slaveID; }
};

#endif // DEV_TEMP_HUMIDITY_H
