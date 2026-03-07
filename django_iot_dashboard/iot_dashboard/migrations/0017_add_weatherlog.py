from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('iot_dashboard', '0016_remove_geminiaisettings_provider'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeatherLog',
            fields=[
                ('id',              models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp',       models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='เวลา')),
                ('city_name',       models.CharField(default='Nakhon Si Thammarat', max_length=100, verbose_name='เมือง')),
                ('location',        models.CharField(blank=True, max_length=100, verbose_name='Location String')),
                ('temperature',     models.FloatField(verbose_name='อุณหภูมิ (°C)')),
                ('feels_like',      models.FloatField(blank=True, null=True, verbose_name='รู้สึกเหมือน (°C)')),
                ('humidity',        models.IntegerField(verbose_name='ความชื้น (%)')),
                ('pressure',        models.IntegerField(blank=True, null=True, verbose_name='ความดันอากาศ (hPa)')),
                ('wind_speed',      models.FloatField(blank=True, null=True, verbose_name='ความเร็วลม (m/s)')),
                ('wind_deg',        models.IntegerField(blank=True, null=True, verbose_name='ทิศลม (°)')),
                ('clouds',          models.IntegerField(blank=True, null=True, verbose_name='เมฆ (%)')),
                ('weather_main',    models.CharField(blank=True, max_length=50, verbose_name='สภาพหลัก')),
                ('weather_desc',    models.CharField(blank=True, max_length=100, verbose_name='รายละเอียด')),
                ('rain_probability',models.FloatField(blank=True, null=True, verbose_name='โอกาสฝน (%)')),
                ('aqi',             models.IntegerField(blank=True, choices=[(1, 'Good'), (2, 'Fair'), (3, 'Moderate'), (4, 'Poor'), (5, 'Very Poor')], null=True, verbose_name='AQI')),
                ('aqi_label',       models.CharField(blank=True, max_length=20, verbose_name='AQI Label')),
                ('pm2_5',           models.FloatField(blank=True, null=True, verbose_name='PM2.5 (μg/m³)')),
                ('pm10',            models.FloatField(blank=True, null=True, verbose_name='PM10 (μg/m³)')),
            ],
            options={
                'verbose_name':        'Weather Log',
                'verbose_name_plural': 'Weather Logs',
                'ordering':            ['-timestamp'],
                'indexes':             [models.Index(fields=['-timestamp'], name='weatherlog_ts_idx')],
            },
        ),
    ]
