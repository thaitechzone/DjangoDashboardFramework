"""
Weather Service Module
Fetches weather data from OpenWeatherMap API for Nakhon Si Thammarat
"""

import os
import requests
import logging
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class WeatherService:
    """Service to fetch weather data from OpenWeatherMap API"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.location = os.getenv('WEATHER_LOCATION', 'Nakhon Si Thammarat,TH')
        self.base_url = 'https://api.openweathermap.org/data/2.5'
        
        if not self.api_key or self.api_key == 'your_openweather_api_key_here':
            logger.warning("OpenWeatherMap API key not configured properly")
    
    def get_current_weather(self) -> Optional[Dict]:
        """
        Get current weather conditions
        
        Returns:
            Dict with current weather data or None if error
            {
                'temperature': float,
                'humidity': float,
                'description': str,
                'feels_like': float,
                'pressure': float,
                'wind_speed': float
            }
        """
        try:
            if not self.api_key or self.api_key == 'your_openweather_api_key_here':
                logger.error("Cannot fetch weather: API key not configured")
                return None
            
            url = f"{self.base_url}/weather"
            params = {
                'q': self.location,
                'appid': self.api_key,
                'units': 'metric',  # Celsius
                'lang': 'th'  # Thai language
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'feels_like': data['main']['feels_like'],
                'pressure': data['main']['pressure'],
                'wind_speed': data['wind']['speed']
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching current weather: {e}")
            return None
        except (KeyError, ValueError) as e:
            logger.error(f"Error parsing weather data: {e}")
            return None
    
    def get_forecast(self, hours: int = 6) -> Optional[Dict]:
        """
        Get weather forecast for next N hours
        
        Args:
            hours: Number of hours to forecast (default 6)
            
        Returns:
            Dict with forecast data or None if error
            {
                'forecasts': [
                    {
                        'time': str,
                        'temperature': float,
                        'humidity': float,
                        'description': str,
                        'rain_probability': float
                    },
                    ...
                ],
                'will_rain': bool,
                'avg_temperature': float,
                'avg_humidity': float,
                'temperature_trend': str  # 'increasing', 'decreasing', 'stable'
            }
        """
        try:
            if not self.api_key or self.api_key == 'your_openweather_api_key_here':
                logger.error("Cannot fetch forecast: API key not configured")
                return None
            
            url = f"{self.base_url}/forecast"
            params = {
                'q': self.location,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'th',
                'cnt': max(1, hours // 3)  # API returns data every 3 hours
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            forecasts = []
            temps = []
            humidities = []
            will_rain = False
            
            for item in data['list']:
                temp = item['main']['temp']
                humidity = item['main']['humidity']
                temps.append(temp)
                humidities.append(humidity)
                
                # Check for rain
                rain_prob = item.get('pop', 0) * 100  # Probability of precipitation
                if rain_prob > 30:  # More than 30% chance of rain
                    will_rain = True
                
                forecasts.append({
                    'time': item['dt_txt'],
                    'temperature': temp,
                    'humidity': humidity,
                    'description': item['weather'][0]['description'],
                    'rain_probability': rain_prob
                })
            
            # Calculate temperature trend
            if len(temps) >= 2:
                first_half_avg = sum(temps[:len(temps)//2]) / (len(temps)//2)
                second_half_avg = sum(temps[len(temps)//2:]) / (len(temps) - len(temps)//2)
                
                if second_half_avg > first_half_avg + 1:
                    temp_trend = 'increasing'
                elif second_half_avg < first_half_avg - 1:
                    temp_trend = 'decreasing'
                else:
                    temp_trend = 'stable'
            else:
                temp_trend = 'stable'
            
            return {
                'forecasts': forecasts,
                'will_rain': will_rain,
                'avg_temperature': sum(temps) / len(temps) if temps else 0,
                'avg_humidity': sum(humidities) / len(humidities) if humidities else 0,
                'temperature_trend': temp_trend
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching weather forecast: {e}")
            return None
        except (KeyError, ValueError) as e:
            logger.error(f"Error parsing forecast data: {e}")
            return None


# Singleton instance
_weather_service = None

def get_weather_service() -> WeatherService:
    """Get singleton instance of WeatherService"""
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService()
    return _weather_service
