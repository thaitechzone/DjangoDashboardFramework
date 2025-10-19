"""
Management command to generate sample sensor data
Simple version - always works!
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from iot_dashboard.models import SensorData

class Command(BaseCommand):
    help = 'Generate sample sensor data (simple version)'

    def add_arguments(self, parser):
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
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing data before generating new data',
        )

    def handle(self, *args, **options):
        count = options['count']
        minutes = options['minutes']
        clear_data = options['clear']

        self.stdout.write('🔧 Generating Sample Sensor Data')
        self.stdout.write('=' * 50)

        # Clear existing data if requested
        if clear_data:
            old_count = SensorData.objects.count()
            SensorData.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'🗑️  Cleared {old_count} existing records'))

        # Generate new data
        base_time = timezone.now()
        generated = 0

        self.stdout.write(f'📊 Generating {count} data points over {minutes} minutes...')

        for i in range(count):
            # Calculate timestamp
            minutes_ago = minutes - (i * minutes / count)
            timestamp = base_time - timedelta(minutes=minutes_ago)

            # Generate realistic values
            temperature = round(25 + random.uniform(-3, 8) + random.uniform(-1, 1), 1)
            humidity = round(60 + random.uniform(-15, 25) + random.uniform(-2, 2), 1)

            # Keep values in realistic range
            temperature = max(15, min(40, temperature))
            humidity = max(20, min(95, humidity))

            # Create sensor data
            SensorData.objects.create(
                device_name="ESP32_DHT22",
                temperature=temperature,
                humidity=humidity,
                timestamp=timestamp
            )

            generated += 1

            # Show progress every 10 records
            if (i + 1) % 10 == 0 or (i + 1) == count:
                self.stdout.write(
                    f'  {i + 1}/{count} - '
                    f'{timestamp.strftime("%H:%M:%S")} - '
                    f'Temp: {temperature}°C, Humidity: {humidity}%'
                )

        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ Generated {generated} sensor data points!'))
        
        # Show time range
        oldest = SensorData.objects.order_by('timestamp').first()
        newest = SensorData.objects.order_by('-timestamp').first()
        
        if oldest and newest:
            self.stdout.write(f'📅 Time range: {oldest.timestamp.strftime("%H:%M:%S")} to {newest.timestamp.strftime("%H:%M:%S")}')
        
        self.stdout.write(f'📊 Total records in database: {SensorData.objects.count()}')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🎯 Data generation complete!'))
