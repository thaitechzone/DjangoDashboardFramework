from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iot_dashboard', '0020_replace_push_intervals_with_global_cooldown'),
    ]

    operations = [
        migrations.RemoveField(model_name='n8npushsettings', name='push_on_sensor'),
        migrations.RemoveField(model_name='n8npushsettings', name='push_on_relay'),
        migrations.RemoveField(model_name='n8npushsettings', name='push_on_alarm'),
        migrations.RemoveField(model_name='n8npushsettings', name='push_on_ai'),
        migrations.RemoveField(model_name='n8npushsettings', name='push_on_weather'),
    ]
