#ifndef DEV_ISO_INPUT_H
#define DEV_ISO_INPUT_H

#include <Arduino.h>

/**
 * @class DevIsoInput
 * @brief คลาสสำหรับจัดการ Isolated Input พร้อม debouncing และ state tracking
 * @details รองรับ Active Low/High และตรวจจับการเปลี่ยนสถานะ
 */
class DevIsoInput {
protected:
  uint8_t pin;
  bool activeHigh;
  bool currentState;
  bool lastState;
  unsigned long lastDebounceTime;
  unsigned long debounceDelay;
  bool lastStableState;

  // Event counters
  unsigned long activationCount;
  unsigned long lastActivationTime;

  // Callback functions
  void (*onActiveCallback)();
  void (*onInactiveCallback)();

public:
  /**
   * @param gpioPin หมายเลขขา GPIO
   * @param activeHigh กำหนดโหมดการทำงาน (default: false = Active Low)
   * @param debounceMs ระยะเวลา debounce ในหน่วย ms (default: 50ms)
   */
  DevIsoInput(uint8_t gpioPin, bool activeHigh = false, unsigned long debounceMs = 50) {
    pin                  = gpioPin;
    this->activeHigh     = activeHigh;
    currentState         = false;
    lastState            = false;
    lastStableState      = false;
    lastDebounceTime     = 0;
    debounceDelay        = debounceMs;
    activationCount      = 0;
    lastActivationTime   = 0;
    onActiveCallback     = nullptr;
    onInactiveCallback   = nullptr;
  }

  /** @brief เริ่มต้นการทำงาน (ตั้งค่า pinMode) */
  virtual void begin() {
    if (activeHigh) {
      pinMode(pin, INPUT);
    } else {
      pinMode(pin, INPUT_PULLUP);
    }
    currentState    = readRawState();
    lastState       = currentState;
    lastStableState = currentState;
  }

  /** @brief อ่านสถานะ raw จาก GPIO (ไม่ผ่าน debounce) */
  bool readRawState() {
    bool reading = digitalRead(pin);
    return activeHigh ? reading : !reading;
  }

  /** @brief อัปเดตสถานะ input (ต้องเรียกใน loop()) */
  virtual bool update() {
    bool reading      = readRawState();
    bool stateChanged = false;

    if (reading != lastState) {
      lastDebounceTime = millis();
    }

    if ((millis() - lastDebounceTime) > debounceDelay) {
      if (reading != lastStableState) {
        lastStableState = reading;
        currentState    = reading;
        stateChanged    = true;

        if (currentState) {
          activationCount++;
          lastActivationTime = millis();
          if (onActiveCallback) onActiveCallback();
        } else {
          if (onInactiveCallback) onInactiveCallback();
        }
      }
    }

    lastState = reading;
    return stateChanged;
  }

  bool isActive()         const { return currentState; }
  bool isInactive()       const { return !currentState; }
  bool wasActivated()     const { return currentState && !lastStableState; }
  bool wasDeactivated()   const { return !currentState && lastStableState; }

  void onActive(void (*cb)())   { onActiveCallback   = cb; }
  void onInactive(void (*cb)()) { onInactiveCallback = cb; }

  uint8_t getPin()                    const { return pin; }
  unsigned long getActivationCount()  const { return activationCount; }
  unsigned long getLastActivationTime() const { return lastActivationTime; }
  unsigned long getDebounceDelay()    const { return debounceDelay; }

  void resetActivationCount()                { activationCount = 0; }
  void setActivationCount(unsigned long count) { activationCount = count; }
  void setDebounceDelay(unsigned long ms)    { debounceDelay = ms; }

  String getStateText() const { return currentState ? "ACTIVE" : "INACTIVE"; }
};

#endif // DEV_ISO_INPUT_H
