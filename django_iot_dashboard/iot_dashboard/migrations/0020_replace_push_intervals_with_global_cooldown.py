from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iot_dashboard', '0019_add_push_interval_to_n8npushsettings'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='n8npushsettings',
            name='push_interval_sensor',
        ),
        migrations.RemoveField(
            model_name='n8npushsettings',
            name='push_interval_weather',
        ),
        migrations.AddField(
            model_name='n8npushsettings',
            name='push_min_interval',
            field=models.PositiveIntegerField(
                default=30,
                verbose_name='ส่งได้ทุกกี่วินาที (Global Cooldown)',
                help_text='รอขั้นต่ำกี่วินาทีระหว่างการ push แต่ละครั้ง (ทุก trigger ใช้ร่วมกัน) — 30 = push ได้สูงสุดทุก 30 วินาที, 0 = ไม่จำกัด',
            ),
        ),
        migrations.AlterField(
            model_name='n8npushsettings',
            name='push_timeout',
            field=models.PositiveIntegerField(
                default=5,
                verbose_name='HTTP Timeout (วินาที)',
                help_text='รอ HTTP response นานสุดกี่วินาที — ถ้า N8N ไม่ตอบภายในเวลานี้จะถือว่า push ล้มเหลว (default 5)',
            ),
        ),
    ]
