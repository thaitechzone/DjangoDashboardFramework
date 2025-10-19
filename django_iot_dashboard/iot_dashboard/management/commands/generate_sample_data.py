"""
Generate Sample Sensor Data - Django Management Command
สร้างข้อมูลตัวอย่างสำหรับทดสอบกราฟ
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random
from iot_dashboard.models import SensorData

class Command(BaseCommand):
    help = 'Generate sample sensor data for testing charts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=120,
            help='Number of data points to generate (default: 120)',
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=2,
            help='Hours of data to generate backwards (default: 2)',
        )

    def handle(self, *args, **options):
        self.stdout.write("🔄 Generating sample sensor data...")
        
        count = options['count']
        hours = options['hours']
        
        # ลบข้อมูลเก่า
        deleted_count = SensorData.objects.all().count()
        SensorData.objects.all().delete()
        self.stdout.write(f"🗑️ Cleared {deleted_count} existing sensor records")
        
        # สร้างข้อมูลย้อนหลัง
        base_time = timezone.now()
        data_points = []
        
        # พารามิเตอร์สำหรับสร้างข้อมูลจำลอง
        base_temp = 28.5  # อุณหภูมิฐาน
        base_humidity = 65.0  # ความชื้นฐาน
        
        minutes_back = hours * 60
        interval = minutes_back / count  # ช่วงเวลาระหว่างข้อมูลแต่ละจุด
        
        for i in range(count):
            timestamp = base_time - timedelta(minutes=i * interval)
            
            # สร้างข้อมูลอุณหภูมิที่มีการเปลี่ยนแปลงตามธรรมชาติ
            temp_variation = random.uniform(-3, 3)  # ความแปรปรวน ±3°C
            temperature = base_temp + temp_variation + (2 * random.random() - 1)  # เพิ่มสัญญาณรบกวน
            
            # สร้างข้อมูลความชื้นที่สัมพันธ์กับอุณหภูมิ
            humidity_variation = random.uniform(-10, 10)  # ความแปรปรวน ±10%
            # ความชื้นมักจะสูงขึ้นเมื่ออุณหภูมิต่ำลง
            humidity = base_humidity + humidity_variation - (temperature - base_temp) * 0.5
            humidity = max(30, min(90, humidity))  # จำกัดช่วง 30-90%
            
            # ปรับให้มีจุดข้อมูลบางจุดที่ผิดปกติ (outliers)
            if random.random() < 0.05:  # 5% โอกาส
                temperature += random.choice([-5, 5])
                humidity += random.choice([-15, 15])
            
            data_points.append(SensorData(
                device_name="ESP32_DHT22_Demo",
                temperature=round(temperature, 1),
                humidity=round(humidity, 1),
                timestamp=timestamp
            ))
        
        # บันทึกข้อมูลทั้งหมด
        SensorData.objects.bulk_create(data_points)
        
        self.stdout.write(
            self.style.SUCCESS(f"✅ Created {len(data_points)} sample data points")
        )
        
        # แสดงสถิติ
        latest = SensorData.objects.order_by('-timestamp').first()
        oldest = SensorData.objects.order_by('timestamp').first()
        
        temp_data = SensorData.objects.filter(temperature__isnull=False)
        humidity_data = SensorData.objects.filter(humidity__isnull=False)
        
        if temp_data.exists():
            temps = [float(s.temperature) for s in temp_data]
            temp_stats = {
                'min': min(temps),
                'max': max(temps),
                'avg': sum(temps) / len(temps)
            }
            
            self.stdout.write(f"🌡️ Temperature Stats:")
            self.stdout.write(f"   Min: {temp_stats['min']:.1f}°C")
            self.stdout.write(f"   Max: {temp_stats['max']:.1f}°C")
            self.stdout.write(f"   Avg: {temp_stats['avg']:.1f}°C")
        
        if humidity_data.exists():
            humidities = [float(s.humidity) for s in humidity_data]
            humidity_stats = {
                'min': min(humidities),
                'max': max(humidities),
                'avg': sum(humidities) / len(humidities)
            }
            
            self.stdout.write(f"💧 Humidity Stats:")
            self.stdout.write(f"   Min: {humidity_stats['min']:.1f}%")
            self.stdout.write(f"   Max: {humidity_stats['max']:.1f}%")
            self.stdout.write(f"   Avg: {humidity_stats['avg']:.1f}%")
        
        self.stdout.write(f"📅 Data Range:")
        self.stdout.write(f"   From: {oldest.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        self.stdout.write(f"   To: {latest.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.stdout.write(
            self.style.SUCCESS("\n🎉 Sample data generation completed!")
        )
        self.stdout.write("📊 You can now view the charts on the dashboard")