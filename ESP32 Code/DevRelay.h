#ifndef DEV_RELAY_H
#define DEV_RELAY_H

#include <Arduino.h>

/**
 * @class DevRelay
 * @brief คลาสสำหรับควบคุม Relay
 * @details รองรับ Active Low (HIGH = OFF, LOW = ON) และ Active High
 */
class DevRelay {
protected:
  uint8_t pin;      // GPIO pin number
  bool state;       // สถานะปัจจุบัน (true = ON, false = OFF)
  bool activeLow;   // โหมดการทำงาน (true = Active Low, false = Active High)

public:
  /**
   * @param gpioPin หมายเลขขา GPIO
   * @param activeLow กำหนดโหมดการทำงาน (default: true = Active Low)
   */
  DevRelay(uint8_t gpioPin, bool activeLow = true) {
    pin             = gpioPin;
    state           = false;
    this->activeLow = activeLow;
  }

  /** @brief เริ่มต้นการทำงาน (ตั้งค่า pinMode และสถานะเริ่มต้น) */
  virtual void begin() {
    pinMode(pin, OUTPUT);
    off(); // เริ่มต้นด้วยสถานะปิด
  }

  /** @brief เปิด Relay */
  virtual void on() {
    state = true;
    digitalWrite(pin, activeLow ? LOW : HIGH);
  }

  /** @brief ปิด Relay */
  virtual void off() {
    state = false;
    digitalWrite(pin, activeLow ? HIGH : LOW);
  }

  /** @brief สลับสถานะ Relay (เปิด <-> ปิด) */
  virtual void toggle() {
    if (state) { off(); } else { on(); }
  }

  /** @brief ตั้งค่าสถานะ Relay */
  virtual void setState(bool newState) {
    if (newState) { on(); } else { off(); }
  }

  /** @brief อ่านสถานะปัจจุบัน @return true = ON, false = OFF */
  virtual bool getState() const { return state; }

  /** @brief อ่านหมายเลขขา GPIO */
  uint8_t getPin() const { return pin; }

  /** @brief ตรวจสอบว่าเป็น Active Low หรือไม่ */
  bool isActiveLow() const { return activeLow; }
};

/**
 * @class DevRelayWithTimer
 * @brief คลาสขยายจาก DevRelay พร้อมฟังก์ชัน Timer
 */
class DevRelayWithTimer : public DevRelay {
private:
  unsigned long timerDuration;  // ระยะเวลา Timer (milliseconds)
  unsigned long timerStart;     // เวลาเริ่มต้น Timer
  bool timerActive;             // สถานะ Timer

public:
  DevRelayWithTimer(uint8_t gpioPin, bool activeLow = true)
    : DevRelay(gpioPin, activeLow) {
    timerDuration = 0;
    timerStart    = 0;
    timerActive   = false;
  }

  /** @brief เปิด Relay พร้อมตั้ง Timer */
  void onWithTimer(unsigned long duration) {
    on();
    timerDuration = duration;
    timerStart    = millis();
    timerActive   = true;
  }

  /** @brief ตรวจสอบและปิด Relay เมื่อหมดเวลา (ต้องเรียกใน loop) */
  bool checkTimer() {
    if (timerActive && state) {
      if (millis() - timerStart >= timerDuration) {
        off();
        timerActive = false;
        return true;
      }
    }
    return false;
  }

  void cancelTimer() { timerActive = false; }
  bool isTimerActive() const { return timerActive; }

  unsigned long getRemainingTime() const {
    if (!timerActive) return 0;
    unsigned long elapsed = millis() - timerStart;
    if (elapsed >= timerDuration) return 0;
    return timerDuration - elapsed;
  }
};

#endif // DEV_RELAY_H
