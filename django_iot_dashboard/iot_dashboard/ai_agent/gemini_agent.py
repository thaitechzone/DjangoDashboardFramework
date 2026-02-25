"""
Gemini Relay Agent - AI Decision Making
Uses Google Gemini AI to analyze weather and decide relay control
"""

import os
import time
import logging
from datetime import datetime, timedelta
from google import genai
from typing import Dict, Tuple, Optional
from django.utils import timezone

logger = logging.getLogger(__name__)

# Cooldown duration when free-tier daily quota is exhausted (1 hour)
QUOTA_COOLDOWN_HOURS = 1

class GeminiRelayAgent:
    """AI Agent using Google Gemini for intelligent relay control"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self._quota_exhausted_until: Optional[datetime] = None  # cooldown tracker
        
        if not self.api_key:
            logger.warning("⚠️ GEMINI_API_KEY not found in environment variables")
            self.client = None
        else:
            try:
                self.client = genai.Client(api_key=self.api_key)
                self.model_name = 'gemini-2.0-flash'
                logger.info(f"✅ Gemini AI configured successfully ({self.model_name})")
            except Exception as e:
                logger.error(f"❌ Error configuring Gemini AI: {e}")
                self.client = None
    
    def analyze_and_decide(self, weather_data: Dict) -> Tuple[str, str, float]:
        """
        Analyze weather data and decide on relay control
        
        Args:
            weather_data: Dictionary containing weather information
            
        Returns:
            Tuple of (decision, reasoning, confidence)
            - decision: 'on' or 'off'
            - reasoning: AI's explanation
            - confidence: 0.0 to 1.0
        """
        if not self.client:
            logger.warning("⚠️ Gemini AI not configured, using fallback logic")
            return self._fallback_decision(weather_data)
        
        # Check if still in quota cooldown period
        if self._quota_exhausted_until and datetime.now() < self._quota_exhausted_until:
            remaining = int((self._quota_exhausted_until - datetime.now()).total_seconds() / 60)
            logger.warning(f"⏳ Quota cooldown active — skipping AI call, {remaining} min remaining. Using fallback logic.")
            return self._fallback_decision(weather_data)
        
        try:
            # Create prompt for Gemini
            prompt = self._create_prompt(weather_data)
            
            logger.info("🤖 Asking Gemini AI for decision...")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            # Successful call — clear any previous cooldown
            self._quota_exhausted_until = None

            # Parse AI response
            decision, reasoning, confidence = self._parse_response(response.text)
            
            logger.info(f"✅ AI Decision: {decision.upper()} (Confidence: {confidence*100:.1f}%)")
            logger.info(f"💭 Reasoning: {reasoning[:100]}...")
            
            return decision, reasoning, confidence
            
        except Exception as e:
            error_str = str(e)
            if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str:
                self._quota_exhausted_until = datetime.now() + timedelta(hours=QUOTA_COOLDOWN_HOURS)
                logger.warning(
                    f"⚠️ Gemini free-tier quota exhausted. "
                    f"AI calls paused for {QUOTA_COOLDOWN_HOURS}h until {self._quota_exhausted_until.strftime('%H:%M:%S')}. "
                    f"Using fallback rule-based logic."
                )
            else:
                logger.error(f"❌ Error getting AI decision: {e}")
            return self._fallback_decision(weather_data)
    
    def _create_prompt(self, weather: Dict) -> str:
        """Create prompt for Gemini AI"""
        
        prompt = f"""You are an intelligent IoT system controller for a relay switch (Relay 2).

**Current Weather Data:**
- Location: {weather.get('location', 'Unknown')}
- Temperature: {weather.get('temperature', 0):.1f}°C (Feels like: {weather.get('feels_like', 0):.1f}°C)
- Humidity: {weather.get('humidity', 0)}%
- Weather: {weather.get('description', 'Unknown')}
- Rain Probability: {weather.get('rain_probability', 0):.1f}%
- Cloud Coverage: {weather.get('clouds', 0)}%
- Wind Speed: {weather.get('wind_speed', 0):.1f} m/s

**Decision Rules:**
1. Turn ON if:
   - Temperature > 32°C AND Humidity < 50% (Hot and dry - needs ventilation)
   - Temperature > 32°C AND Humidity > 70% (Hot and humid - needs cooling)
   - Rain probability < 60% (Low rain - safe to operate)
   - Extreme weather conditions

2. Turn OFF if:
   - Temperature < 30°C AND Humidity > 60% (Cool and humid - save energy)
   - Rain probability > 60% (High rain - protect equipment)
   - Thunderstorm or heavy rain expected
   - Good weather conditions with no need for ventilation

3. Consider:
   - Comfort level (feels_like temperature)
   - Energy efficiency
   - Weather trends

**Your Task:**
Decide whether to turn Relay 2 ON or OFF based on the weather data.

**Response Format (IMPORTANT - Follow exactly):**
DECISION: [ON or OFF]
CONFIDENCE: [0-100]
REASONING: [Your detailed explanation in 2-3 sentences]

Example:
DECISION: ON
CONFIDENCE: 85
REASONING: Temperature is 35°C with 80% humidity, making it very uncomfortable. High rain probability of 75% suggests incoming rain. Turning on relay for cooling/protection.

Now analyze and respond:"""

        return prompt
    
    def _parse_response(self, response_text: str) -> Tuple[str, str, float]:
        """
        Parse Gemini AI response
        
        Args:
            response_text: Raw response from Gemini
            
        Returns:
            Tuple of (decision, reasoning, confidence)
        """
        try:
            lines = response_text.strip().split('\n')
            
            decision = 'off'
            confidence = 0.5
            reasoning = 'AI analysis completed'
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('DECISION:'):
                    decision_text = line.replace('DECISION:', '').strip().lower()
                    decision = 'on' if 'on' in decision_text else 'off'
                
                elif line.startswith('CONFIDENCE:'):
                    conf_text = line.replace('CONFIDENCE:', '').strip()
                    # Extract number from text
                    conf_num = ''.join(filter(str.isdigit, conf_text))
                    if conf_num:
                        confidence = float(conf_num) / 100.0
                        confidence = max(0.0, min(1.0, confidence))
                
                elif line.startswith('REASONING:'):
                    reasoning = line.replace('REASONING:', '').strip()
                    # Get remaining lines as reasoning
                    idx = lines.index(line)
                    if idx + 1 < len(lines):
                        reasoning += ' ' + ' '.join(lines[idx+1:])
                    reasoning = reasoning.strip()
            
            return decision, reasoning, confidence
            
        except Exception as e:
            logger.error(f"❌ Error parsing AI response: {e}")
            logger.error(f"Response text: {response_text}")
            return 'off', 'Error parsing AI response', 0.5
    
    def _fallback_decision(self, weather: Dict) -> Tuple[str, str, float]:
        """
        Fallback decision logic when AI is not available
        
        Args:
            weather: Weather data dictionary
            
        Returns:
            Tuple of (decision, reasoning, confidence)
        """
        temp = weather.get('temperature', 0)
        humidity = weather.get('humidity', 0)
        rain_prob = weather.get('rain_probability', 0)
        
        # Simple rule-based logic
        if temp > 32 and humidity < 50:
            decision = 'on'
            reasoning = f'Hot and dry conditions ({temp}°C, {humidity}%). Needs ventilation. Using fallback logic.'
            confidence = 0.7
        elif temp > 32 and humidity > 70:
            decision = 'on'
            reasoning = f'Hot and humid conditions ({temp}°C, {humidity}%). Needs cooling. Using fallback logic.'
            confidence = 0.7
        elif rain_prob < 60 and temp > 30:
            decision = 'on'
            reasoning = f'Low rain probability ({rain_prob}%) and warm weather. Safe to operate. Using fallback logic.'
            confidence = 0.6
        elif rain_prob > 60:
            decision = 'off'
            reasoning = f'High rain probability ({rain_prob}%). Protect equipment. Using fallback logic.'
            confidence = 0.7
        elif temp < 30 and humidity > 60:
            decision = 'off'
            reasoning = f'Cool and humid conditions ({temp}°C, {humidity}%). Save energy. Using fallback logic.'
            confidence = 0.7
        else:
            decision = 'off'
            reasoning = 'Weather conditions are moderate. Using fallback logic.'
            confidence = 0.5
        
        logger.info(f"🔧 Fallback Decision: {decision.upper()} (Confidence: {confidence*100:.1f}%)")
        return decision, reasoning, confidence
