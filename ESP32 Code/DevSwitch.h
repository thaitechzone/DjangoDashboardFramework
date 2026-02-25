#ifndef DEV_SWITCH_H
#define DEV_SWITCH_H

#include <Arduino.h>

/**
 * @class DevSwitch
 * @brief คลาสสำหรับจัดการปุ่มกดพร้อม debouncing และ edge detection
 * @details รองรับ Active Low/High, callback functions, long-press detection
 */
class DevSwitch {
protected:
  uint8_t pin;
  bool activeHigh;
  bool currentState;
  bool lastState;
  unsigned long lastDebounceTime;
  unsigned long debounceDelay;
  bool lastStableState;

  // Long press detection
  unsigned long pressStartTime;
  unsigned long longPressDelay;
  bool longPressTriggered;

  // Callback functions
  void (*onPressCallback)();
  void (*onReleaseCallback)();
  void (*onClickCallback)();
  void (*onLongPressCallback)();

public:
  /**
   * @param gpioPin หมายเลขขา GPIO
   * @param activeHigh กำหนดโหมดการทำงาน (default: false = Active Low)
   * @param debounceMs ระยะเวลา debounce ในหน่วย ms (default: 50ms)
   * @param longPressMs ระยะเวลา long press (default: 1000ms)
   */
  DevSwitch(uint8_t gpioPin, bool activeHigh = false,
            unsigned long debounceMs = 50, unsigned long longPressMs = 1000) {
    pin                 = gpioPin;
    this->activeHigh    = activeHigh;
    currentState        = false;
    lastState           = false;
    lastStableState     = false;
    lastDebounceTime    = 0;
    debounceDelay       = debounceMs;
    pressStartTime      = 0;
    longPressDelay      = longPressMs;
    longPressTriggered  = false;
    onPressCallback     = nullptr;
    onReleaseCallback   = nullptr;
    onClickCallback     = nullptr;
    onLongPressCallback = nullptr;
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

  /** @brief อัปเดตสถานะปุ่ม (ต้องเรียกใน loop()) */
  virtual bool update() {
    bool reading     = readRawState();
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
          pressStartTime     = millis();
          longPressTriggered = false;
          if (onPressCallback) onPressCallback();
        } else {
          if (onReleaseCallback) onReleaseCallback();
          if (!longPressTriggered && onClickCallback) onClickCallback();
        }
      }
    }

    if (currentState && !longPressTriggered) {
      if ((millis() - pressStartTime) >= longPressDelay) {
        longPressTriggered = true;
        if (onLongPressCallback) onLongPressCallback();
      }
    }

    lastState = reading;
    return stateChanged;
  }

  bool isPressed()    const { return currentState; }
  bool isReleased()   const { return !currentState; }
  bool isLongPressing() const { return currentState && longPressTriggered; }

  unsigned long getPressDuration() const {
    if (currentState) return millis() - pressStartTime;
    return 0;
  }

  void onPress(void (*cb)())     { onPressCallback     = cb; }
  void onRelease(void (*cb)())   { onReleaseCallback   = cb; }
  void onClick(void (*cb)())     { onClickCallback     = cb; }
  void onLongPress(void (*cb)()) { onLongPressCallback = cb; }

  uint8_t getPin()             const { return pin; }
  unsigned long getDebounceDelay() const { return debounceDelay; }
  void setDebounceDelay(unsigned long ms) { debounceDelay = ms; }
  void setLongPressDelay(unsigned long ms) { longPressDelay = ms; }
  unsigned long getLongPressDelay() const { return longPressDelay; }
};

#endif // DEV_SWITCH_H
