from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
import pytz
from iot_dashboard.models import SensorData

class Command(BaseCommand):
    help = 'Generate fresh sensor data with current Thai time'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before generating new data',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=30,
            help='Number of data points to generate (default: 30)',
        )
        parser.add_argument(
            '--minutes',
            type=int,
            default=30,
            help='Time span in minutes (default: 30)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting fresh data generation...'))
        
        # Clear existing data if requested
        if options['clear']:
            count = SensorData.objects.count()
            SensorData.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f'🗑️  Cleared {count} existing records')
            )
        
        # Setup parameters
        count = options['count']
        minutes = options['minutes']
        
        # Generate data
        base_time = timezone.now()
        generated = 0
        
        self.stdout.write(f'📊 Generating {count} data points over {minutes} minutes...')
        
        for i in range(count):
            # Calculate timestamp (going back in time)
            timestamp = base_time - timedelta(minutes=minutes-i*(minutes/count))
            
            # Generate realistic sensor values
            base_temp = 26  # Base temperature
            temp_variation = random.uniform(-3, 6)  # Daily variation
            temp_noise = random.uniform(-1, 1)      # Random noise
            temperature = round(base_temp + temp_variation + temp_noise, 1)
            
            base_humidity = 65  # Base humidity
            humidity_variation = random.uniform(-15, 15)  # Daily variation
            humidity_noise = random.uniform(-3, 3)        # Random noise
            humidity = round(base_humidity + humidity_variation + humidity_noise, 1)
            
            # Ensure realistic ranges
            temperature = max(20, min(35, temperature))
            humidity = max(30, min(90, humidity))
            
            # Create sensor data
            sensor_data = SensorData.objects.create(
                device_name="ESP32_DHT22",
                temperature=temperature,
                humidity=humidity,
                timestamp=timestamp
            )
            
            generated += 1
            
            # Show progress
            if i % 10 == 0 or i == count - 1:
                thai_tz = pytz.timezone('Asia/Bangkok')
                thai_time = timestamp.astimezone(thai_tz)
                self.stdout.write(
                    f'  📈 {i+1:3d}/{count} - {thai_time.strftime("%H:%M:%S")} - '
                    f'Temp: {temperature}°C, Humidity: {humidity}%'
                )
        
        # Summary
        thai_tz = pytz.timezone('Asia/Bangkok')
        start_time = (base_time - timedelta(minutes=minutes)).astimezone(thai_tz)
        end_time = base_time.astimezone(thai_tz)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Generated {generated} sensor data points!\n'
                f'📅 Time range: {start_time.strftime("%H:%M:%S")} to {end_time.strftime("%H:%M:%S")}\n'
                f'🌡️  Temperature range: 20-35°C\n'
                f'💧 Humidity range: 30-90%\n'
                f'📊 Total records in database: {SensorData.objects.count()}'
            )
        )