#!/usr/bin/env python
"""
Test script to verify timezone configuration
"""
import os
import django
from datetime import datetime
import pytz

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()

from django.utils import timezone

# Test timezone functions
print("🕐 Timezone Test Results")
print("=" * 50)

# Current UTC time
utc_now = timezone.now()
print(f"UTC Time: {utc_now}")

# Thai timezone
thai_tz = pytz.timezone('Asia/Bangkok')
thai_time = utc_now.astimezone(thai_tz)
print(f"Thai Time: {thai_time}")

# Format Thai time
formatted_thai = thai_time.strftime("%d/%m/%Y %H:%M:%S")
print(f"Formatted Thai: {formatted_thai}")

# JavaScript compatible format
js_format = thai_time.strftime("%Y-%m-%d %H:%M:%S")
print(f"JS Format: {js_format}")

# System time for comparison
import time
system_time = datetime.now()
print(f"System Time: {system_time}")

# Time difference
time_diff = thai_time.replace(tzinfo=None) - system_time
print(f"Time Difference: {time_diff}")

print("\n✅ Timezone test completed!")