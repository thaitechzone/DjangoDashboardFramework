from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iot_dashboard', '0008_deviceconfig'),
    ]

    operations = [
        migrations.AddField(
            model_name='deviceconfig',
            name='ds18b20_temperature',
            field=models.FloatField(
                blank=True,
                null=True,
                verbose_name='DS18B20 Temperature (°C)',
                help_text='ค่าล่าสุดจาก DS18B20 sensor ที่รับผ่าน MQTT',
            ),
        ),
        migrations.AddField(
            model_name='deviceconfig',
            name='ds18b20_updated_at',
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name='DS18B20 Last Updated',
            ),
        ),
    ]
