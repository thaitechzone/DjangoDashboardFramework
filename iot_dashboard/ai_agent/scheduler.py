"""
AI Agent Scheduler Module
Background task scheduler for periodic AI analysis and Relay 2 control
"""

import os
import logging
from datetime import datetime
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class AIAgentScheduler:
    """Background scheduler for AI Agent periodic analysis"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.interval_minutes = int(os.getenv('AI_AGENT_INTERVAL_MINUTES', 15))
        self.is_running = False
        
        logger.info(f"AIAgentScheduler initialized with {self.interval_minutes} minute interval")
    
    def start(self):
        """Start the scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        try:
            # Add job to run AI analysis periodically
            self.scheduler.add_job(
                func=self.run_ai_analysis,
                trigger=IntervalTrigger(minutes=self.interval_minutes),
                id='ai_agent_analysis',
                name='AI Agent Relay 2 Analysis',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.is_running = True
            
            logger.info(f"✅ AI Agent Scheduler started - will run every {self.interval_minutes} minutes")
            
        except Exception as e:
            logger.error(f"❌ Error starting scheduler: {e}")
    
    def stop(self):
        """Stop the scheduler"""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        try:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("AI Agent Scheduler stopped")
            
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    def run_ai_analysis(self):
        """
        Main workflow for AI analysis and Relay 2 control
        
        Steps:
        1. Fetch latest sensor data (Temperature, Humidity)
        2. Get weather forecast for Nakhon Si Thammarat
        3. Run AI analysis using Gemini
        4. Compare decision with current Relay 2 status
        5. Log the decision to database
        6. Control Relay 2 if needed (via MQTT)
        """
        try:
            logger.info("🤖 Starting AI analysis...")
            
            # Import here to avoid circular imports
            from iot_dashboard.models import SensorData, Relay, AIDecisionLog
            from iot_dashboard.ai_agent.weather_service import get_weather_service
            from iot_dashboard.ai_agent.gemini_agent import get_gemini_agent
            from iot_dashboard.mqtt_manager import get_mqtt_manager
            
            # Step 1: Get latest sensor data
            latest_sensor = SensorData.objects.first()
            if not latest_sensor:
                logger.warning("⚠️ No sensor data available, skipping AI analysis")
                return
            
            temperature = latest_sensor.temperature
            humidity = latest_sensor.humidity
            
            if temperature is None or humidity is None:
                logger.warning("⚠️ Invalid sensor data (None values), skipping")
                return
            
            logger.info(f"📊 Sensor Data - Temp: {temperature}°C, Humidity: {humidity}%")
            
            # Step 2: Get weather forecast
            weather_service = get_weather_service()
            weather_forecast = weather_service.get_forecast(hours=6)
            
            if weather_forecast:
                logger.info(f"🌦️ Weather Forecast - Trend: {weather_forecast.get('temperature_trend')}, Rain: {weather_forecast.get('will_rain')}")
            else:
                logger.warning("⚠️ Could not fetch weather forecast, AI will use only sensor data")
            
            # Step 3: Run AI analysis
            gemini_agent = get_gemini_agent()
            ai_result = gemini_agent.analyze_and_decide(
                temperature=temperature,
                humidity=humidity,
                weather_forecast=weather_forecast
            )
            
            decision = ai_result['decision']  # 'ON' or 'OFF'
            confidence = ai_result['confidence']
            reasoning = ai_result['reasoning']
            
            logger.info(f"🧠 AI Decision: {decision} (confidence: {confidence:.2f})")
            logger.info(f"💭 Reasoning: {reasoning}")
            
            # Step 4: Get current Relay 2 status
            relay = Relay.objects.first()
            if not relay:
                # Create relay if doesn't exist
                relay = Relay.objects.create(name="Main Relay Controller")
            
            current_relay2_status = relay.relay2_status
            new_relay2_status = (decision == 'ON')
            
            logger.info(f"⚡ Current Relay 2: {'ON' if current_relay2_status else 'OFF'} → New: {'ON' if new_relay2_status else 'OFF'}")
            
            # Step 5: Log the decision
            log_entry = AIDecisionLog.objects.create(
                current_temperature=temperature,
                current_humidity=humidity,
                weather_forecast=weather_forecast or {},
                decision=decision,
                confidence=confidence,
                reasoning=reasoning,
                relay2_previous_status=current_relay2_status,
                relay2_new_status=new_relay2_status,
                action_taken=(current_relay2_status != new_relay2_status)
            )
            
            logger.info(f"📝 Decision logged (ID: {log_entry.id})")
            
            # Step 6: Control Relay 2 if status changed
            if current_relay2_status != new_relay2_status:
                logger.info(f"🎛️ Relay 2 status changing: {'OFF' if current_relay2_status else 'ON'} → {'ON' if new_relay2_status else 'OFF'}")
                
                # Update relay status in database
                relay.relay2_status = new_relay2_status
                relay.save()
                
                # Send MQTT command to ESP32
                mqtt_manager = get_mqtt_manager()
                if mqtt_manager and mqtt_manager.is_connected():
                    try:
                        # Send command to control Relay 2
                        topic = "iot/relay/control"
                        message = {
                            "relay": 2,
                            "status": "ON" if new_relay2_status else "OFF",
                            "source": "AI_AGENT",
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        import json
                        mqtt_manager.publish(topic, json.dumps(message))
                        logger.info(f"✅ MQTT command sent to Relay 2: {message['status']}")
                        
                    except Exception as e:
                        logger.error(f"❌ Error sending MQTT command: {e}")
                else:
                    logger.warning("⚠️ MQTT not connected, Relay 2 status updated in DB only")
            else:
                logger.info(f"✔️ No change needed - Relay 2 already {'ON' if current_relay2_status else 'OFF'}")
            
            logger.info("✅ AI analysis completed successfully\n")
            
        except Exception as e:
            logger.error(f"❌ Error in AI analysis: {e}", exc_info=True)
    
    def trigger_manual_analysis(self) -> dict:
        """
        Manually trigger AI analysis (for API endpoint)
        
        Returns:
            dict: Result of the analysis
        """
        try:
            logger.info("🔄 Manual AI analysis triggered")
            self.run_ai_analysis()
            return {
                'success': True,
                'message': 'AI analysis triggered successfully'
            }
        except Exception as e:
            logger.error(f"Error in manual analysis: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def get_status(self) -> dict:
        """
        Get scheduler status
        
        Returns:
            dict: Current status information
        """
        return {
            'is_running': self.is_running,
            'interval_minutes': self.interval_minutes,
            'next_run': self._get_next_run_time()
        }
    
    def _get_next_run_time(self) -> Optional[str]:
        """Get next scheduled run time"""
        if not self.is_running:
            return None
        
        job = self.scheduler.get_job('ai_agent_analysis')
        if job and job.next_run_time:
            return job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")
        
        return None


# Singleton instance
_ai_scheduler = None

def get_ai_scheduler() -> AIAgentScheduler:
    """Get singleton instance of AIAgentScheduler"""
    global _ai_scheduler
    if _ai_scheduler is None:
        _ai_scheduler = AIAgentScheduler()
    return _ai_scheduler
