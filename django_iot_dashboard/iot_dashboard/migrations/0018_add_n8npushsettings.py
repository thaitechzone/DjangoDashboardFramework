from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iot_dashboard', '0017_add_weatherlog'),
    ]

    operations = [
        migrations.CreateModel(
            name='N8NPushSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_enabled', models.BooleanField(
                    default=False,
                    verbose_name='เปิดใช้งาน N8N Push',
                    help_text='เปิดเพื่อให้ Django ส่ง event ไปยัง N8N ทุกครั้งที่มีข้อมูลใหม่',
                )),
                ('webhook_snapshot', models.URLField(
                    max_length=500, blank=True, default='',
                    verbose_name='Snapshot Webhook URL',
                    help_text='URL หลัก: http://YOUR_N8N:5678/webhook/iot-snapshot',
                )),
                ('push_timeout', models.PositiveIntegerField(
                    default=5,
                    verbose_name='Timeout (วินาที)',
                    help_text='รอ HTTP response นานสุดกี่วินาที (default 5)',
                )),
                ('push_on_sensor', models.BooleanField(default=True, verbose_name='ส่งเมื่อได้รับ Sensor data')),
                ('push_on_relay',  models.BooleanField(default=True, verbose_name='ส่งเมื่อ Relay เปลี่ยน')),
                ('push_on_alarm',  models.BooleanField(default=True, verbose_name='ส่งเมื่อ Alarm เปลี่ยนสถานะ')),
                ('push_on_ai',     models.BooleanField(default=True, verbose_name='ส่งเมื่อ AI ตัดสินใจ')),
                ('push_on_weather',models.BooleanField(default=True, verbose_name='ส่งเมื่อบันทึก Weather Log')),
                ('last_push_at',   models.DateTimeField(null=True, blank=True, verbose_name='Push ล่าสุด')),
                ('last_push_ok',   models.BooleanField(null=True, blank=True, verbose_name='ผลล่าสุด')),
                ('last_push_msg',  models.CharField(max_length=500, blank=True, verbose_name='ข้อความล่าสุด')),
            ],
            options={
                'verbose_name': 'N8N Push Settings',
                'verbose_name_plural': 'N8N Push Settings',
            },
        ),
    ]
