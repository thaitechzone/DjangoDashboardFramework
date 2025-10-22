"""
Weather Service - OpenWeatherMap API Integration
Fetches current weather data for Nakhon Si Thammarat
"""

import os
import requests
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.location = os.getenv('WEATHER_LOCATION', 'Nakhon Si Thammarat,TH')
        self.base_url = 'http://api.openweathermap.org/data/2.5/weather'
        
        if not self.api_key:
            logger.warning("⚠️ OPENWEATHER_API_KEY not found in environment variables")
    
    def get_current_weather(self) -> Optional[Dict]:
        """
        Fetch current weather data
        
        Returns:
            Dict with weather data or None if failed
        """
        if not self.api_key:
            logger.error("❌ Cannot fetch weather: API key not configured")
            return None
        
        try:
            params = {
                'q': self.location,
                'appid': self.api_key,
                'units': 'metric'  # Celsius
            }
            
            logger.info(f"🌤️ Fetching weather for {self.location}...")
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant information
            weather_info = {
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'main': data['weather'][0]['main'],
                'feels_like': data['main']['feels_like'],
                'pressure': data['main']['pressure'],
                'wind_speed': data['wind']['speed'],
                'clouds': data['clouds']['all'],
                'location': self.location
            }
            
            # Calculate rain probability based on conditions
            weather_info['rain_probability'] = self._estimate_rain_probability(data)
            
            logger.info(f"✅ Weather fetched: {weather_info['temperature']}°C, {weather_info['description']}")
            return weather_info
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error fetching weather: {e}")
            return None
        except KeyError as e:
            logger.error(f"❌ Error parsing weather data: {e}")
            return None
    
    def _estimate_rain_probability(self, data: Dict) -> float:
        """
        Estimate rain probability based on weather conditions
        
        Args:
            data: Raw weather data from API
            
        Returns:
            Rain probability (0-100)
        """
        # Check if there's actual rain data
        if 'rain' in data:
            # If raining, probability is high
            return 90.0
        
        # Otherwise estimate based on conditions
        main = data['weather'][0]['main'].lower()
        description = data['weather'][0]['description'].lower()
        humidity = data['main']['humidity']
        clouds = data['clouds']['all']
        
        # Base probability on weather type
        if 'rain' in main or 'rain' in description:
            return 80.0
        elif 'drizzle' in main or 'drizzle' in description:
            return 60.0
        elif 'thunderstorm' in main or 'storm' in description:
            return 95.0
        elif 'clouds' in main or 'cloud' in description:
            # Cloud coverage + humidity
            base = clouds * 0.5
            if humidity > 80:
                base += 20
            return min(base, 70.0)
        elif 'clear' in main:
            return 10.0
        else:
            # Default based on humidity
            if humidity > 85:
                return 40.0
            elif humidity > 70:
                return 25.0
            else:
                return 15.0
