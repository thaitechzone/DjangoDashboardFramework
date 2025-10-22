import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

print("=" * 50)
print("Environment Variables Test")
print("=" * 50)
print(f"GEMINI_API_KEY: {os.getenv('GEMINI_API_KEY')[:30]}...")
print(f"OPENWEATHER_API_KEY: {os.getenv('OPENWEATHER_API_KEY')}")
print(f"WEATHER_LOCATION: {os.getenv('WEATHER_LOCATION')}")
print(f"AI_AGENT_INTERVAL_MINUTES: {os.getenv('AI_AGENT_INTERVAL_MINUTES')}")
print("=" * 50)
