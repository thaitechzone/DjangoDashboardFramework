# -*- coding: utf-8 -*-
"""
Generate Sample Sensor Data
สร้างข้อมูลตัวอย่างสำหรับทดสอบกราฟ
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# Setup Django
project_path = os.path.join(os.path.dirname(__file__), 'django_iot_dashboard')
sys.path.append(project_path)
os.chdir(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_iot_dashboard.settings')
django.setup()

from iot_dashboard.models import SensorData

def generate_sample_data():
    """สร้างข้อมูลตัวอย่างสำหรับทดสอบ"""
    
    print("🔄 Generating sample sensor data...")
    
    # ลบข้อมูลเก่า
    SensorData.objects.all().delete()
    print("🗑️ Cleared existing sensor data")
    
    # สร้างข้อมูลย้อนหลัง 2 ชั่วโมง
    base_time = datetime.now()
    data_points = []
    
    # พารามิเตอร์สำหรับสร้างข้อมูลจำลอง
    base_temp = 28.5  # อุณหภูมิฐาน
    base_humidity = 65.0  # ความชื้นฐาน
    
    for i in range(120):  # 120 จุดข้อมูล (ทุก 1 นาที ย้อนหลัง 2 ชั่วโมง)
        timestamp = base_time - timedelta(minutes=i)
        
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
    
    print(f"✅ Created {len(data_points)} sample data points")
    
    # แสดงสถิติ
    latest = SensorData.objects.order_by('-timestamp').first()
    oldest = SensorData.objects.order_by('timestamp').first()
    
    temp_data = SensorData.objects.filter(temperature__isnull=False)
    humidity_data = SensorData.objects.filter(humidity__isnull=False)
    
    if temp_data.exists():
        temps = [s.temperature for s in temp_data]
        temp_stats = {
            'min': min(temps),
            'max': max(temps),
            'avg': sum(temps) / len(temps)
        }
        
        print(f"🌡️ Temperature Stats:")
        print(f"   Min: {temp_stats['min']:.1f}°C")
        print(f"   Max: {temp_stats['max']:.1f}°C")
        print(f"   Avg: {temp_stats['avg']:.1f}°C")
    
    if humidity_data.exists():
        humidities = [s.humidity for s in humidity_data]
        humidity_stats = {
            'min': min(humidities),
            'max': max(humidities),
            'avg': sum(humidities) / len(humidities)
        }
        
        print(f"💧 Humidity Stats:")
        print(f"   Min: {humidity_stats['min']:.1f}%")
        print(f"   Max: {humidity_stats['max']:.1f}%")
        print(f"   Avg: {humidity_stats['avg']:.1f}%")
    
    print(f"📅 Data Range:")
    print(f"   From: {oldest.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   To: {latest.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n🎉 Sample data generation completed!")
    print("📊 You can now view the charts on the dashboard")

if __name__ == "__main__":
    try:
        generate_sample_data()
    except Exception as e:
        print(f"❌ Error generating sample data: {e}")