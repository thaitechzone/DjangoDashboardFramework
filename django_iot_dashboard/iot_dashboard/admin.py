from django.contrib import admin
from .models import Device, SensorData, Relay

# Register your models here.

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_on', 'last_updated', 'created_at')
    list_filter = ('is_on', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'last_updated')

@admin.register(Relay)
class RelayAdmin(admin.ModelAdmin):
    list_display = ('name', 'relay1_status', 'relay2_status', 'relay3_status', 'last_updated', 'created_at')
    list_filter = ('relay1_status', 'relay2_status', 'relay3_status', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'last_updated')
    fieldsets = (
        ('Relay Information', {
            'fields': ('name',)
        }),
        ('Relay Status', {
            'fields': ('relay1_status', 'relay2_status', 'relay3_status'),
            'description': 'Control RELAY switches status'
        }),
        ('Timestamps', {
            'fields': ('last_updated', 'created_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ('device_name', 'temperature', 'humidity', 'timestamp')
    list_filter = ('device_name', 'timestamp')
    search_fields = ('device_name',)
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
