"""
Weather Service - OpenWeatherMap API Integration
Fetches current weather and air quality data
"""

import os
import requests
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API"""
    
    def __init__(self):
        # อ่านจาก DB (WeatherAPISettings) ก่อน แล้ว fallback ที่ env var
        try:
            from iot_dashboard.models import WeatherAPISettings
            db_cfg = WeatherAPISettings.get_settings()
            self.api_key  = db_cfg.api_key or os.getenv('OPENWEATHER_API_KEY', '')
            self.location = db_cfg.location or os.getenv('WEATHER_LOCATION', 'Nakhon Si Thammarat,TH')
            self.units    = db_cfg.units or 'metric'
            self.is_enabled = db_cfg.is_enabled
        except Exception:
            self.api_key  = os.getenv('OPENWEATHER_API_KEY', '')
            self.location = os.getenv('WEATHER_LOCATION', 'Nakhon Si Thammarat,TH')
            self.units    = 'metric'
            self.is_enabled = True

        self.base_url = 'http://api.openweathermap.org/data/2.5/weather'
        self.air_pollution_url = 'http://api.openweathermap.org/data/2.5/air_pollution'
        
        if not self.api_key:
            logger.warning("⚠️ OPENWEATHER_API_KEY not configured (DB or env)")
    
    def get_current_weather(self) -> Optional[Dict]:
        """
        Fetch current weather data
        
        Returns:
            Dict with weather data or None if failed
        """
        if not self.api_key:
            logger.error("❌ Cannot fetch weather: API key not configured")
            return None
        
        if not self.is_enabled:
            logger.info("⏸️ Weather API disabled in settings")
            return None
        
        try:
            params = {
                'q': self.location,
                'appid': self.api_key,
                'units': self.units
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
                'wind_deg': data['wind'].get('deg', 0),
                'clouds': data['clouds']['all'],
                'location': self.location,
                'city_name': data.get('name', self.location.split(',')[0]),
                'lat': data['coord']['lat'],
                'lon': data['coord']['lon'],
            }
            
            # Calculate rain probability based on conditions
            weather_info['rain_probability'] = self._estimate_rain_probability(data)
            
            # Fetch Air Quality (AQI / PM2.5)
            air_quality = self._get_air_quality(weather_info['lat'], weather_info['lon'])
            if air_quality:
                weather_info.update(air_quality)
            
            logger.info(f"✅ Weather fetched: {weather_info['temperature']}°C, {weather_info['description']}")
            return weather_info
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error fetching weather: {e}")
            return None
        except KeyError as e:
            logger.error(f"❌ Error parsing weather data: {e}")
            return None
    
    def _get_air_quality(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Fetch Air Quality Index (AQI) and PM2.5 from OpenWeatherMap Air Pollution API

        Returns:
            Dict with aqi, aqi_label, pm2_5, pm10 or None if failed
        """
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
            }
            response = requests.get(self.air_pollution_url, params=params, timeout=10)
            response.raise_for_status()
            aq_data = response.json()

            aqi_value = aq_data['list'][0]['main']['aqi']  # 1-5
            components = aq_data['list'][0]['components']

            aqi_labels = {1: 'Good', 2: 'Fair', 3: 'Moderate', 4: 'Poor', 5: 'Very Poor'}

            logger.info(f"✅ Air quality fetched: AQI={aqi_value}, PM2.5={components.get('pm2_5')}")
            return {
                'aqi': aqi_value,
                'aqi_label': aqi_labels.get(aqi_value, 'Unknown'),
                'pm2_5': components.get('pm2_5', 0),
                'pm10': components.get('pm10', 0),
            }
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch air quality: {e}")
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
