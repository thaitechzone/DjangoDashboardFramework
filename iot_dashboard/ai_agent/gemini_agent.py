"""
Gemini AI Agent Module
Uses Google Gemini AI to make intelligent decisions for Relay 2 control
"""

import os
import json
import logging
from typing import Dict, Optional
from dotenv import load_dotenv

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class GeminiRelayAgent:
    """AI Agent using Google Gemini for intelligent Relay 2 control"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model = None
        
        if genai and self.api_key and self.api_key != 'your_gemini_api_key_here':
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini AI initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing Gemini AI: {e}")
        else:
            if not genai:
                logger.warning("google-generativeai package not available")
            else:
                logger.warning("Gemini API key not configured properly")
    
    def analyze_and_decide(
        self, 
        temperature: float, 
        humidity: float, 
        weather_forecast: Optional[Dict] = None
    ) -> Dict:
        """
        Analyze sensor data and weather forecast to decide Relay 2 status
        
        Args:
            temperature: Current indoor temperature (Celsius)
            humidity: Current indoor humidity (%)
            weather_forecast: Weather forecast data from WeatherService
            
        Returns:
            Dict with decision result:
            {
                'decision': 'ON' or 'OFF',
                'confidence': float (0.0-1.0),
                'reasoning': str (explanation in Thai)
            }
        """
        # If AI not available, use fallback logic
        if not self.model:
            logger.info("Using fallback decision logic (AI not available)")
            return self._fallback_decision(temperature, humidity, weather_forecast)
        
        try:
            # Prepare prompt for Gemini
            prompt = self._build_prompt(temperature, humidity, weather_forecast)
            
            # Get AI response
            response = self.model.generate_content(prompt)
            
            # Parse response
            result = self._parse_response(response.text)
            
            logger.info(f"AI Decision: {result['decision']} (confidence: {result['confidence']:.2f})")
            logger.info(f"Reasoning: {result['reasoning']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            logger.info("Falling back to rule-based decision")
            return self._fallback_decision(temperature, humidity, weather_forecast)
    
    def _build_prompt(
        self, 
        temperature: float, 
        humidity: float, 
        weather_forecast: Optional[Dict]
    ) -> str:
        """Build prompt for Gemini AI"""
        
        # Base information
        prompt = f"""คุณเป็น AI ผู้ช่วยในการควบคุมระบบ Relay 2 สำหรับระบบควบคุมอุณหภูมิและความชื้น

ข้อมูลปัจจุบัน:
- อุณหภูมิภายใน: {temperature}°C
- ความชื้นภายใน: {humidity}%
"""
        
        # Add weather forecast if available
        if weather_forecast:
            prompt += f"""
ข้อมูลพยากรณ์อากาศ นครศรีธรรมราช:
- แนวโน้มอุณหภูมิ: {weather_forecast.get('temperature_trend', 'ไม่ทราบ')}
- อุณหภูมิเฉลี่ย 6 ชั่วโมงข้างหน้า: {weather_forecast.get('avg_temperature', 'N/A'):.1f}°C
- ความชื้นเฉลี่ย: {weather_forecast.get('avg_humidity', 'N/A'):.1f}%
- โอกาสฝนตก: {'มี' if weather_forecast.get('will_rain', False) else 'ไม่มี'}
"""
        
        # Decision rules
        prompt += """
กฎการตัดสินใจ:
1. ถ้าอุณหภูมิ > 32°C และความชื้น > 75% → ควรเปิด Relay 2 (ON)
2. ถ้าพยากรณ์อากาศบอกว่าอุณหภูมิจะสูงขึ้น → พิจารณาเปิด Relay 2 เพื่อเตรียมพร้อม
3. ถ้าอุณหภูมิ < 28°C → ควรปิด Relay 2 (OFF)
4. ถ้ามีโอกาสฝนตก → พิจารณาปิด Relay 2 (เพราะอุณหภูมิจะลดลง)

โปรดวิเคราะห์ข้อมูลและตัดสินใจว่าควร:
- เปิด Relay 2 (ON)
- ปิด Relay 2 (OFF)

ตอบกลับในรูปแบบ JSON เท่านั้น:
{
    "decision": "ON" หรือ "OFF",
    "confidence": ค่าความมั่นใจ 0.0-1.0,
    "reasoning": "คำอธิบายเหตุผลการตัดสินใจภาษาไทย"
}
"""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> Dict:
        """Parse AI response and extract decision"""
        
        try:
            # Try to find JSON in response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                result = json.loads(json_str)
                
                # Validate response
                if 'decision' in result and 'confidence' in result and 'reasoning' in result:
                    # Ensure decision is uppercase
                    result['decision'] = result['decision'].upper()
                    
                    # Clamp confidence to 0.0-1.0
                    result['confidence'] = max(0.0, min(1.0, float(result['confidence'])))
                    
                    return result
            
            # If parsing fails, log and use fallback
            logger.warning(f"Could not parse AI response as JSON: {response_text}")
            raise ValueError("Invalid response format")
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"Error parsing AI response: {e}")
            raise
    
    def _fallback_decision(
        self, 
        temperature: float, 
        humidity: float, 
        weather_forecast: Optional[Dict]
    ) -> Dict:
        """
        Rule-based fallback decision when AI is not available
        
        Simple rules:
        - Temp > 32°C AND Humidity > 75% → ON
        - Forecast shows increasing temp → ON
        - Temp < 28°C → OFF
        - Rain forecast → OFF
        """
        
        decision = 'OFF'
        confidence = 0.7  # Moderate confidence for rule-based
        reasoning = []
        
        # Rule 1: High temperature and humidity
        if temperature > 32 and humidity > 75:
            decision = 'ON'
            confidence = 0.9
            reasoning.append(f"อุณหภูมิสูง ({temperature}°C) และความชื้นสูง ({humidity}%)")
        
        # Rule 2: Check weather forecast
        elif weather_forecast:
            if weather_forecast.get('temperature_trend') == 'increasing':
                decision = 'ON'
                confidence = 0.7
                reasoning.append("แนวโน้มอุณหภูมิกำลังเพิ่มขึ้น")
            
            if weather_forecast.get('will_rain', False):
                decision = 'OFF'
                confidence = 0.8
                reasoning.append("มีโอกาสฝนตก อุณหภูมิจะลดลง")
        
        # Rule 3: Low temperature
        if temperature < 28:
            decision = 'OFF'
            confidence = 0.85
            reasoning.append(f"อุณหภูมิต่ำ ({temperature}°C)")
        
        # Build reasoning text
        if not reasoning:
            reasoning.append(f"อุณหภูมิปกติ ({temperature}°C), ความชื้น ({humidity}%)")
        
        reasoning_text = "ใช้กฎอัตโนมัติ: " + ", ".join(reasoning)
        
        return {
            'decision': decision,
            'confidence': confidence,
            'reasoning': reasoning_text
        }


# Singleton instance
_gemini_agent = None

def get_gemini_agent() -> GeminiRelayAgent:
    """Get singleton instance of GeminiRelayAgent"""
    global _gemini_agent
    if _gemini_agent is None:
        _gemini_agent = GeminiRelayAgent()
    return _gemini_agent
