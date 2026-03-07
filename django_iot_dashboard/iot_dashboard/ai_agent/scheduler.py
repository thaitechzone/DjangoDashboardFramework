"""
AI Agent Scheduler
Runs periodic weather analysis and relay control
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.utils import timezone
from django.conf import settings
from datetime import datetime, timedelta
import os

from .weather_service import WeatherService
from .gemini_agent import GeminiRelayAgent

logger = logging.getLogger(__name__)

class AIAgentScheduler:
    """Scheduler for periodic AI analysis and weather logging"""
    
    WEATHER_LOG_INTERVAL_MINUTES = 15  # บันทึกสภาพอากาศทุกๆ 15 นาที

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.weather_service = WeatherService()
        self.ai_agent = GeminiRelayAgent()
        self.is_running = False
        
        # Get interval from DB first, fallback to environment variable
        try:
            from iot_dashboard.models import GeminiAISettings
            self.interval_minutes = GeminiAISettings.get_settings().interval_minutes
        except Exception:
            self.interval_minutes = int(os.getenv('AI_AGENT_INTERVAL_MINUTES', '15'))
    
    def start(self):
        """Start the scheduler"""
        if self.is_running:
            logger.warning("⚠️ AI Agent Scheduler already running")
            return
        
        try:
            # Delay first run by 60s to avoid DB access during app initialization (AppConfig.ready())
            first_run_time = datetime.now() + timedelta(seconds=60)

            # Job 1: AI analysis + relay control (configurable interval)
            self.scheduler.add_job(
                func=self.analyze_and_control,
                trigger=IntervalTrigger(minutes=self.interval_minutes, start_date=first_run_time),
                id='ai_weather_analysis',
                name='AI Weather Analysis and Relay Control',
                replace_existing=True
            )

            # Job 2: Weather log every 15 minutes (independent of AI interval)
            weather_log_start = datetime.now() + timedelta(seconds=90)
            self.scheduler.add_job(
                func=self.log_weather,
                trigger=IntervalTrigger(
                    minutes=self.WEATHER_LOG_INTERVAL_MINUTES,
                    start_date=weather_log_start,
                ),
                id='weather_logger',
                name='Weather Logger (Nakhon Si Thammarat — every 15 min)',
                replace_existing=True,
            )
            
            self.scheduler.start()
            self.is_running = True
            
            logger.info(f"✅ AI Agent Scheduler started successfully!")
            logger.info(f"🕐 Analysis interval: Every {self.interval_minutes} minutes")
            logger.info(f"🌤️ Weather log interval: Every {self.WEATHER_LOG_INTERVAL_MINUTES} minutes")
            logger.info(f"⏳ First analysis scheduled at: {first_run_time.strftime('%H:%M:%S')} (60s delay)")
            
        except Exception as e:
            logger.error(f"❌ Error starting AI Agent Scheduler: {e}")
    
    def stop(self):
        """Stop the scheduler"""
        if not self.is_running:
            return
        
        try:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("🛑 AI Agent Scheduler stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping AI Agent Scheduler: {e}")
    
    def log_weather(self):
        """
        บันทึกข้อมูลสภาพอากาศ Nakhon Si Thammarat ลงฐานข้อมูลทุก 15 นาที
        ทำงานแยกต่างหากจาก AI analysis เพื่อให้ข้อมูลสมบูรณ์เสมอ
        """
        logger.info("🌤️ Weather logger: fetching current weather...")
        try:
            from iot_dashboard.models import WeatherLog
            weather_data = self.weather_service.get_current_weather()
            if not weather_data:
                logger.warning("⚠️ Weather logger: no data returned, skip")
                return
            entry = WeatherLog.record_from_weather_data(weather_data)
            logger.info(
                f"✅ WeatherLog saved [id={entry.pk}] "
                f"{entry.city_name} {entry.temperature:.1f}°C {entry.humidity}% "
                f"{entry.weather_desc} AQI={entry.aqi_label or '-'}"
            )

            # ── N8N Snapshot Push: weather logged ────────────────────────
            try:
                from iot_dashboard import n8n_pusher
                n8n_pusher.push_snapshot('weather', {
                    'log_id':           entry.pk,
                    'temperature':      entry.temperature,
                    'humidity':         entry.humidity,
                    'rain_probability': entry.rain_probability,
                    'aqi':              entry.aqi,
                    'aqi_label':        entry.aqi_label,
                    'weather_desc':     entry.weather_desc,
                })
            except Exception as push_err:
                logger.warning(f"⚠️ N8N snapshot push (weather) failed: {push_err}")

        except Exception as e:
            logger.error(f"❌ Weather logger error: {e}", exc_info=True)

    def analyze_and_control(self):
        """
        Main analysis function:
        1. Fetch weather data
        2. Ask AI for decision
        3. Control relay
        4. Log decision
        """
        logger.info("=" * 50)
        logger.info("🤖 Starting AI Weather Analysis...")
        logger.info("=" * 50)
        
        try:
            # Import here to avoid circular imports
            from iot_dashboard.models import Relay, AIDecisionLog
            from iot_dashboard.mqtt_manager import send_relay_command
            
            # 1. Fetch weather
            weather_data = self.weather_service.get_current_weather()
            if not weather_data:
                logger.error("❌ Failed to fetch weather data")
                return
            
            # 2. Get AI decision
            decision, reasoning, confidence = self.ai_agent.analyze_and_decide(weather_data)
            
            # 3. Control relay
            relay_num = 2  # Control Relay 2
            command = 'ON' if decision == 'on' else 'OFF'
            
            logger.info(f"📡 Sending command to Relay {relay_num}: {command}")
            success, message = send_relay_command(
                relay_num, command,
                source='ai_agent',
                reason=f"AI decision (confidence={confidence*100:.1f}%): {reasoning[:200]}"
            )
            
            if success:
                logger.info(f"✅ Relay command successful: {message}")
                
                # Update database
                relay_controller = Relay.objects.first()
                if relay_controller:
                    relay_controller.relay2_status = (decision == 'on')
                    relay_controller.last_updated = timezone.now()
                    relay_controller.save()
                    logger.info(f"✅ Database updated: Relay 2 = {relay_controller.relay2_status}")
            else:
                logger.error(f"❌ Relay command failed: {message}")
            
            # 4. Log decision
            AIDecisionLog.objects.create(
                decision=decision,
                reasoning=reasoning,
                confidence=confidence,
                weather_data=weather_data,
                relay_status=(decision == 'on'),
                command_sent=success
            )
            
            logger.info("✅ Decision logged to database")

            # ── N8N Snapshot Push: AI decision ───────────────────────────
            try:
                from iot_dashboard import n8n_pusher
                n8n_pusher.push_snapshot('ai', {
                    'decision':          decision,
                    'confidence_pct':    round(confidence * 100, 1),
                    'reasoning_summary': reasoning[:300],
                    'relay_number':      relay_num,
                    'command':           command,
                    'command_success':   success,
                })
            except Exception as push_err:
                logger.warning(f"⚠️ N8N snapshot push (ai) failed: {push_err}")

            logger.info("=" * 50)
            logger.info(f"🎯 Summary: {decision.upper()} | Confidence: {confidence*100:.1f}% | Success: {success}")
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"❌ Error in AI analysis: {e}", exc_info=True)
    
    def get_status(self):
        """Get scheduler status"""
        return {
            'is_running': self.is_running,
            'interval_minutes': self.interval_minutes,
            'next_run': self.get_next_run_time()
        }
    
    def get_next_run_time(self):
        """Get next scheduled run time"""
        if not self.is_running:
            return None
        
        try:
            job = self.scheduler.get_job('ai_weather_analysis')
            if job and job.next_run_time:
                return job.next_run_time
        except:
            pass
        
        return None
    
    def trigger_manual_analysis(self):
        """Trigger AI analysis manually (for testing/debugging)"""
        logger.info("🔧 Manual AI analysis triggered")
        try:
            self.analyze_and_control()
            return {
                'success': True,
                'message': 'AI analysis completed successfully'
            }
        except Exception as e:
            logger.error(f"❌ Manual analysis failed: {e}")
            return {
                'success': False,
                'message': str(e)
            }

    def trigger_manual_weather_log(self):
        """Trigger weather log manually (for testing/debugging)"""
        logger.info("🔧 Manual weather log triggered")
        try:
            self.log_weather()
            return {'success': True, 'message': 'Weather log saved successfully'}
        except Exception as e:
            logger.error(f"❌ Manual weather log failed: {e}")
            return {'success': False, 'message': str(e)}

# Global scheduler instance
_scheduler = None

def get_scheduler():
    """Get global scheduler instance"""
    global _scheduler
    if _scheduler is None:
        _scheduler = AIAgentScheduler()
    return _scheduler

def get_ai_scheduler():
    """Get global AI scheduler instance (alias for compatibility)"""
    return get_scheduler()

def start_scheduler():
    """Start global scheduler"""
    scheduler = get_scheduler()
    scheduler.start()
    return scheduler

def stop_scheduler():
    """Stop global scheduler"""
    global _scheduler
    if _scheduler:
        _scheduler.stop()
        _scheduler = None
