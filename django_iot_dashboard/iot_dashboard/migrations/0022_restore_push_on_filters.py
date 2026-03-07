from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iot_dashboard', '0021_remove_push_on_filters'),
    ]

    operations = [
        migrations.AddField(
            model_name='n8npushsettings',
            name='push_on_sensor',
            field=models.BooleanField(default=True, verbose_name='ส่งเมื่อได้รับ Sensor data',
                                      help_text='Push ทุกครั้งที่ ESP32 ส่ง DHT22/DS18B20 มา (บ่อยที่สุด)'),
        ),
        migrations.AddField(
            model_name='n8npushsettings',
            name='push_on_relay',
            field=models.BooleanField(default=True, verbose_name='ส่งเมื่อ Relay เปลี่ยน',
                                      help_text='Push เมื่อ relay state เปลี่ยนแปลง'),
        ),
        migrations.AddField(
            model_name='n8npushsettings',
            name='push_on_alarm',
            field=models.BooleanField(default=True, verbose_name='ส่งเมื่อ Alarm เปลี่ยนสถานะ',
                                      help_text='Push เมื่อ alarm activated / deactivated'),
        ),
        migrations.AddField(
            model_name='n8npushsettings',
            name='push_on_ai',
            field=models.BooleanField(default=True, verbose_name='ส่งเมื่อ AI ตัดสินใจ',
                                      help_text='Push ทุกครั้งที่ AI agent วิเคราะห์และส่งคำสั่ง'),
        ),
        migrations.AddField(
            model_name='n8npushsettings',
            name='push_on_weather',
            field=models.BooleanField(default=True, verbose_name='ส่งเมื่อบันทึก Weather Log',
                                      help_text='Push ทุก 15 นาทีเมื่อ weather logger บันทึก'),
        ),
    ]
