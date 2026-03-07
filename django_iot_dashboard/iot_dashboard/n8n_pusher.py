# -*- coding: utf-8 -*-
"""
N8N Webhook Pusher (Approach A — Push / Real-time)
===================================================
ส่ง HTTP POST ไปยัง N8N webhook ทันทีที่มีเหตุการณ์เกิดขึ้น
ทุก push ทำงานใน background thread เพื่อไม่บล็อก MQTT / scheduler loop

Configuration (.env):
    N8N_PUSH_ENABLED=true
    N8N_WEBHOOK_SENSOR=http://YOUR_N8N:5678/webhook/iot-sensor
    N8N_WEBHOOK_RELAY=http://YOUR_N8N:5678/webhook/iot-relay
    N8N_WEBHOOK_ALARM=http://YOUR_N8N:5678/webhook/iot-alarm
    N8N_WEBHOOK_AI=http://YOUR_N8N:5678/webhook/iot-ai
    N8N_WEBHOOK_WEATHER=http://YOUR_N8N:5678/webhook/iot-weather
    N8N_PUSH_TIMEOUT=5    # seconds per request

Event types and triggers:
    sensor  → ทุกครั้งที่ ESP32 ส่ง DHT22/DS18B20 data มาถึง
    relay   → ทุกครั้งที่ relay state เปลี่ยน (ESP32 confirm หรือ Dashboard สั่ง)
    alarm   → ทุกครั้งที่ alarm activated / deactivated
    ai      → ทุกครั้งที่ AI agent ตัดสินใจและส่งคำสั่ง
    weather → ทุกครั้งที่ weather logger บันทึก WeatherLog (ทุก 15 นาที)
"""

import json
import logging
import os
import threading
import time
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

# ─── rate limiter (in-memory, persists for process lifetime) ─────────────────
# _last_push[trigger] = monotonic timestamp of the last successful push dispatch
_last_push: dict = {}
_push_lock = threading.Lock()

# ─────────────────────────────────────────────────────────────────────────────
# Config helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get_env(key: str, default: str = '') -> str:
    """ดึงค่าจาก env ก่อน django settings (ใช้ได้ตั้งแต่ก่อน django fully ready)"""
    try:
        from django.conf import settings
        return getattr(settings, key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)


def _get_db_settings():
    """ดึง N8NPushSettings จาก DB (คืน None ถ้า DB ยังไม่พร้อม)"""
    try:
        from iot_dashboard.models import N8NPushSettings
        return N8NPushSettings.get_settings()
    except Exception:
        return None


def is_enabled() -> bool:
    cfg = _get_db_settings()
    if cfg is not None:
        return cfg.is_enabled
    return _get_env('N8N_PUSH_ENABLED', 'false').lower() in ('1', 'true', 'yes')


def _webhook_url(event: str) -> str:
    """คืน webhook URL สำหรับ event type (sensor/relay/alarm/ai/weather)"""
    mapping = {
        'sensor':  'N8N_WEBHOOK_SENSOR',
        'relay':   'N8N_WEBHOOK_RELAY',
        'alarm':   'N8N_WEBHOOK_ALARM',
        'ai':      'N8N_WEBHOOK_AI',
        'weather': 'N8N_WEBHOOK_WEATHER',
    }
    env_key = mapping.get(event)
    if not env_key:
        return ''
    return _get_env(env_key, '')


def _timeout() -> float:
    try:
        return float(_get_env('N8N_PUSH_TIMEOUT', '5'))
    except ValueError:
        return 5.0


# ─────────────────────────────────────────────────────────────────────────────
# Core push (runs in background thread)
# ─────────────────────────────────────────────────────────────────────────────

def _do_push(url: str, payload: dict):
    """HTTP POST ไปยัง N8N webhook — เรียกใน background thread เสมอ"""
    try:
        body = json.dumps(payload, default=str, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                'Content-Type': 'application/json; charset=utf-8',
                'User-Agent': 'DjangoDashboard-N8NPusher/1.0',
            },
            method='POST',
        )
        timeout = _timeout()
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.getcode()
            if status == 200:
                logger.debug(f"✅ N8N push OK [{url}] {status}")
            else:
                logger.warning(f"⚠️ N8N push returned {status} [{url}]")
    except urllib.error.URLError as e:
        logger.warning(f"⚠️ N8N push failed [{url}]: {e.reason}")
    except Exception as e:
        logger.error(f"❌ N8N push error [{url}]: {e}")


def push_event(event: str, payload: dict):
    """
    ส่ง event ไปยัง N8N webhook ใน background thread
    ถ้า N8N_PUSH_ENABLED=false หรือ URL ไม่ได้ตั้ง → ข้ามทันที

    Args:
        event   : 'sensor' | 'relay' | 'alarm' | 'ai' | 'weather'
        payload : dict ที่จะส่งเป็น JSON body
    """
    if not is_enabled():
        return

    url = _webhook_url(event)
    if not url:
        logger.debug(f"⏭️  N8N push skipped: URL for '{event}' not configured")
        return

    # เพิ่ม metadata มาตรฐาน
    from django.utils import timezone
    try:
        import pytz
        bkk = pytz.timezone('Asia/Bangkok')
        ts = timezone.now().astimezone(bkk).strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        ts = str(timezone.now())

    full_payload = {
        'event': event,
        'timestamp': ts,
        'source': 'django_iot_dashboard',
        **payload,
    }

    t = threading.Thread(
        target=_do_push,
        args=(url, full_payload),
        daemon=True,
        name=f'n8n-push-{event}',
    )
    t.start()
    logger.debug(f"🚀 N8N push queued: event='{event}' url={url}")


# ─────────────────────────────────────────────────────────────────────────────
# Typed helpers — ใช้เรียกจาก callbacks/scheduler
# ─────────────────────────────────────────────────────────────────────────────

def push_sensor(sensor_data_obj):
    """
    Push เมื่อได้รับ sensor data ใหม่ (SensorData model instance)
    เรียกจาก: mqtt_callbacks.handle_sensor_data_message / handle_ds18b20_message
    """
    push_event('sensor', {
        'device_name': sensor_data_obj.device_name,
        'temperature': sensor_data_obj.temperature,
        'humidity':    sensor_data_obj.humidity,
        'ds18b20':     sensor_data_obj.ds18b20_temperature,
        'sensor_id':   sensor_data_obj.id,
    })


def push_relay(relay_num: int, new_state: bool, old_state: bool, source: str, reason: str = ''):
    """
    Push เมื่อ relay state เปลี่ยน
    เรียกจาก: mqtt_callbacks.handle_relay_state_message (เฉพาะเมื่อ old != new)
    """
    push_event('relay', {
        'relay_number': relay_num,
        'new_state':    'ON' if new_state else 'OFF',
        'old_state':    'ON' if old_state else 'OFF',
        'changed':      old_state != new_state,
        'source':       source,
        'reason':       reason,
    })


def push_alarm(active: bool, reason: str = ''):
    """
    Push เมื่อ alarm เปลี่ยนสถานะ (activated / deactivated)
    เรียกจาก: mqtt_callbacks.handle_sensor_data_message (ภาย threshold check)
    """
    push_event('alarm', {
        'alarm_active': active,
        'alarm_state':  'ACTIVATED' if active else 'DEACTIVATED',
        'reason':       reason,
    })


def push_ai_decision(decision: str, confidence: float, reasoning: str,
                     relay_num: int, command: str, success: bool):
    """
    Push เมื่อ AI agent ตัดสินใจและส่งคำสั่ง
    เรียกจาก: scheduler.analyze_and_control
    """
    push_event('ai', {
        'decision':          decision,
        'confidence_pct':    round(confidence * 100, 1),
        'reasoning_summary': reasoning[:300],
        'relay_number':      relay_num,
        'command':           command,
        'command_success':   success,
    })


def push_weather(weather_log_obj):
    """
    Push เมื่อ WeatherLog บันทึกสำเร็จ (ทุก 15 นาที)
    เรียกจาก: scheduler.log_weather
    """
    push_event('weather', {
        'log_id':           weather_log_obj.pk,
        'city_name':        weather_log_obj.city_name,
        'temperature':      weather_log_obj.temperature,
        'feels_like':       weather_log_obj.feels_like,
        'humidity':         weather_log_obj.humidity,
        'pressure':         weather_log_obj.pressure,
        'wind_speed':       weather_log_obj.wind_speed,
        'clouds':           weather_log_obj.clouds,
        'weather_main':     weather_log_obj.weather_main,
        'weather_desc':     weather_log_obj.weather_desc,
        'rain_probability': weather_log_obj.rain_probability,
        'aqi':              weather_log_obj.aqi,
        'aqi_label':        weather_log_obj.aqi_label,
        'pm2_5':            weather_log_obj.pm2_5,
        'pm10':             weather_log_obj.pm10,
    })


# ─────────────────────────────────────────────────────────────────────────────
# All-in-one Snapshot Push  (Primary method — single webhook)
# ─────────────────────────────────────────────────────────────────────────────

def push_snapshot(trigger: str, trigger_data: dict = None):
    """
    Push snapshot รวมข้อมูลทั้งหมดไปยัง N8N webhook เดียว ทันทีที่มี event เกิดขึ้น

    Payload ประกอบด้วย:
      trigger          : event ที่ทำให้เกิดการ push (sensor/relay/alarm/ai/weather)
      trigger_data     : ข้อมูลสั้นๆ ของ event นั้น
      sensor_latest    : ค่า sensor ล่าสุด
      relay_status     : สถานะ relay ทั้ง 3 ตัว
      alarm            : สถานะ alarm ปัจจุบัน
      ai_latest        : AI decision ล่าสุด
      weather_latest   : สภาพอากาศล่าสุด

    Config (.env):
      N8N_WEBHOOK_SNAPSHOT=http://YOUR_N8N:5678/webhook/iot-snapshot
    """
    if not is_enabled():
        return

    cfg = _get_db_settings()
    if cfg is not None:
        url = cfg.webhook_snapshot.strip()
        # ตรวจ trigger filter
        _TRIGGER_FLAGS = {
            'sensor':  'push_on_sensor',
            'relay':   'push_on_relay',
            'alarm':   'push_on_alarm',
            'ai':      'push_on_ai',
            'weather': 'push_on_weather',
        }
        flag = _TRIGGER_FLAGS.get(trigger)
        if flag and not getattr(cfg, flag, True):
            logger.debug(f"⏭️  N8N snapshot push skipped: {flag}=False (trigger='{trigger}')")
            return
        # ตรวจ global rate limit — ทุก trigger ใช้ cooldown ร่วมกัน
        min_interval = getattr(cfg, 'push_min_interval', 30)
        if min_interval > 0:
            with _push_lock:
                elapsed = time.monotonic() - _last_push.get('_global', 0)
                if elapsed < min_interval:
                    logger.debug(
                        f"⏱️  N8N snapshot skipped (global cooldown): trigger='{trigger}' "
                        f"elapsed={elapsed:.0f}s < {min_interval}s"
                    )
                    return
                _last_push['_global'] = time.monotonic()
    else:
        url = _get_env('N8N_WEBHOOK_SNAPSHOT', '')

    if not url:
        logger.debug("⏭️  N8N snapshot push skipped: N8N_WEBHOOK_SNAPSHOT not configured")
        return

    def _build_and_push():
        try:
            from django.utils import timezone
            import pytz
            from iot_dashboard.models import (
                SensorData, Relay, ThresholdSetting, AIDecisionLog, WeatherLog
            )

            bkk = pytz.timezone('Asia/Bangkok')

            def _fmt(dt):
                if not dt:
                    return None
                try:
                    return dt.astimezone(bkk).strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    return str(dt)

            now = timezone.now()
            ts = now.astimezone(bkk).strftime('%Y-%m-%d %H:%M:%S')

            sensor   = SensorData.objects.order_by('-timestamp').first()
            relay    = Relay.objects.first()
            thresh   = ThresholdSetting.get_or_create_default()
            ai_log   = AIDecisionLog.objects.order_by('-timestamp').first()
            weather  = WeatherLog.objects.order_by('-timestamp').first()

            payload = {
                'event':        'snapshot',
                'trigger':      trigger,
                'trigger_data': trigger_data or {},
                'timestamp':    ts,
                'source':       'django_iot_dashboard',
                'sensor_latest': {
                    'device_name': sensor.device_name,
                    'temperature': sensor.temperature,
                    'humidity':    sensor.humidity,
                    'ds18b20':     sensor.ds18b20_temperature,
                    'timestamp':   _fmt(sensor.timestamp),
                } if sensor else None,
                'relay_status': {
                    'relay1':       relay.relay1_status if relay else None,
                    'relay2':       relay.relay2_status if relay else None,
                    'relay3':       relay.relay3_status if relay else None,
                    'last_updated': _fmt(relay.last_updated) if relay else None,
                },
                'alarm': {
                    'active':         thresh.alarm_active,
                    'reason':         thresh.alarm_reason,
                    'mode':           thresh.mode,
                    'last_triggered': _fmt(thresh.last_triggered),
                } if thresh else None,
                'ai_latest': {
                    'decision':          ai_log.decision,
                    'confidence_pct':    round(float(ai_log.confidence) * 100, 1),
                    'reasoning_summary': ai_log.reasoning[:300],
                    'relay_status':      ai_log.relay_status,
                    'command_sent':      ai_log.command_sent,
                    'timestamp':         _fmt(ai_log.timestamp),
                } if ai_log else None,
                'weather_latest': {
                    'city_name':        weather.city_name,
                    'temperature':      weather.temperature,
                    'feels_like':       weather.feels_like,
                    'humidity':         weather.humidity,
                    'pressure':         weather.pressure,
                    'wind_speed':       weather.wind_speed,
                    'clouds':           weather.clouds,
                    'weather_main':     weather.weather_main,
                    'weather_desc':     weather.weather_desc,
                    'rain_probability': weather.rain_probability,
                    'aqi':              weather.aqi,
                    'aqi_label':        weather.aqi_label,
                    'pm2_5':            weather.pm2_5,
                    'pm10':             weather.pm10,
                    'timestamp':        _fmt(weather.timestamp),
                } if weather else None,
            }

            # ─ do push ─
            ok = True
            msg = ''
            try:
                _do_push(url, payload)
                logger.debug(f"✅ N8N snapshot push sent: trigger='{trigger}'")
            except Exception as push_err:
                ok = False
                msg = str(push_err)[:500]
                logger.error(f"❌ N8N snapshot push error (trigger='{trigger}'): {push_err}")

            # ─ update last_push status in DB ─
            try:
                from iot_dashboard.models import N8NPushSettings
                N8NPushSettings.objects.filter(pk=1).update(
                    last_push_at=now,
                    last_push_ok=ok,
                    last_push_msg=msg,
                )
            except Exception:
                pass

        except Exception as e:
            logger.error(f"❌ N8N snapshot build error (trigger='{trigger}'): {e}")

    t = threading.Thread(
        target=_build_and_push,
        daemon=True,
        name=f'n8n-snapshot-{trigger}',
    )
    t.start()
    logger.debug(f"🚀 N8N snapshot push queued: trigger='{trigger}'")
