from django.shortcuts import render
from .models import Device

def dashboard_view(request):
    # Get the LED device object. Use get_or_create to avoid errors on first run.
    led_device, created = Device.objects.get_or_create(name="Onboard LED")
    
    context = {
        'led': led_device
    }
    return render(request, 'iot_dashboard/dashboard.html', context)
