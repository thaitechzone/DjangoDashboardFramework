"""
AI Agent Package for Intelligent Relay Control

This package provides AI-powered decision making for Relay 2 control
based on indoor sensor data and weather forecast.

Components:
- WeatherService: Fetches weather data from OpenWeatherMap
- GeminiRelayAgent: AI decision engine using Google Gemini
- AIAgentScheduler: Background task scheduler
"""

__version__ = '1.0.0'
__all__ = ['WeatherService', 'GeminiRelayAgent', 'AIAgentScheduler']
