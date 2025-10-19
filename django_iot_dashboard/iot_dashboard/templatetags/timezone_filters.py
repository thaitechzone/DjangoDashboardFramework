from django import template
from django.utils import timezone
import pytz

register = template.Library()

@register.filter
def thai_time(value):
    """Convert datetime to Thai timezone"""
    if value:
        thai_tz = pytz.timezone('Asia/Bangkok')
        if timezone.is_aware(value):
            return value.astimezone(thai_tz)
        else:
            return thai_tz.localize(value)
    return value

@register.filter
def thai_time_format(value, format_string="%H:%M:%S"):
    """Convert datetime to Thai timezone and format"""
    if value:
        thai_tz = pytz.timezone('Asia/Bangkok')
        if timezone.is_aware(value):
            thai_time = value.astimezone(thai_tz)
        else:
            thai_time = thai_tz.localize(value)
        return thai_time.strftime(format_string)
    return ""