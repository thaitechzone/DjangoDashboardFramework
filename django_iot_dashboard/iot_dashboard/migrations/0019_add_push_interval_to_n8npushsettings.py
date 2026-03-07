from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iot_dashboard', '0018_add_n8npushsettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='n8npushsettings',
            name='push_interval_sensor',
            field=models.PositiveIntegerField(
                default=60,
                verbose_name='Sensor cooldown (วินาที)',
                help_text='รอขั้นต่ำกี่วินาทีระหว่าง sensor push — ESP32 ส่งทุกไม่กี่วินาที, 60 = push ทุก 1 นาที, 0 = push ทุก message',
            ),
        ),
        migrations.AddField(
            model_name='n8npushsettings',
            name='push_interval_weather',
            field=models.PositiveIntegerField(
                default=0,
                verbose_name='Weather cooldown (วินาที)',
                help_text='รอขั้นต่ำระหว่าง weather push (ปกติ 0 เพราะ scheduler ทำทุก 15 นาทีอยู่แล้ว)',
            ),
        ),
    ]
