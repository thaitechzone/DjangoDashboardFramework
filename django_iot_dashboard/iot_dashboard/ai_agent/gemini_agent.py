"""
Gemini Relay Agent - AI Decision Making
Uses Google Gemini AI to analyze weather and decide relay control
"""

import os
import logging
import google.generativeai as genai
from typing import Dict, Tuple, Optional
from django.utils import timezone

logger = logging.getLogger(__name__)

class GeminiRelayAgent:
    """AI Agent using Google Gemini for intelligent relay control"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            logger.warning("⚠️ GEMINI_API_KEY not found in environment variables")
            self.model = None
        else:
            try:
                genai.configure(api_key=self.api_key)
                # Use gemini-1.5-flash (faster, free tier) or gemini-1.5-pro (more capable)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("✅ Gemini AI configured successfully (gemini-1.5-flash)")
            except Exception as e:
                logger.error(f"❌ Error configuring Gemini AI: {e}")
                self.model = None
    
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
        if not self.model:
            logger.warning("⚠️ Gemini AI not configured, using fallback logic")
            return self._fallback_decision(weather_data)
        
        try:
            # Create prompt for Gemini
            prompt = self._create_prompt(weather_data)
            
            logger.info("🤖 Asking Gemini AI for decision...")
            response = self.model.generate_content(prompt)
            
            # Parse AI response
            decision, reasoning, confidence = self._parse_response(response.text)
            
            logger.info(f"✅ AI Decision: {decision.upper()} (Confidence: {confidence*100:.1f}%)")
            logger.info(f"💭 Reasoning: {reasoning[:100]}...")
            
            return decision, reasoning, confidence
            
        except Exception as e:
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
   - Temperature > 32°C AND Humidity > 70%
   - Rain probability > 60%
   - Thunderstorm or heavy rain expected
   - Extreme weather conditions

2. Turn OFF if:
   - Temperature < 30°C AND Humidity < 60%
   - Clear weather with low rain probability
   - Good weather conditions

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
        if temp > 32 and humidity > 70:
            decision = 'on'
            reasoning = f'High temperature ({temp}°C) and humidity ({humidity}%). Using fallback logic.'
            confidence = 0.7
        elif rain_prob > 60:
            decision = 'on'
            reasoning = f'High rain probability ({rain_prob}%). Using fallback logic.'
            confidence = 0.6
        elif temp < 30 and humidity < 60:
            decision = 'off'
            reasoning = f'Comfortable temperature ({temp}°C) and humidity ({humidity}%). Using fallback logic.'
            confidence = 0.7
        else:
            decision = 'off'
            reasoning = 'Weather conditions are moderate. Using fallback logic.'
            confidence = 0.5
        
        logger.info(f"🔧 Fallback Decision: {decision.upper()} (Confidence: {confidence*100:.1f}%)")
        return decision, reasoning, confidence
