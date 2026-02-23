# Generated manually for DeviceConfig model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iot_dashboard', '0007_remove_aidecisionlog_action_taken_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_name', models.CharField(
                    default='tti_board_001',
                    max_length=50,
                    verbose_name='Device Name (DEVICE_ID)',
                    help_text='ชื่อบอร์ดที่ตั้งใน #define DEVICE_NAME ของ firmware เช่น tti_board_001',
                )),
                ('mqtt_broker', models.CharField(
                    default='broker.hivemq.com',
                    max_length=100,
                    verbose_name='MQTT Broker',
                )),
                ('mqtt_port', models.IntegerField(
                    default=1883,
                    verbose_name='MQTT Port',
                )),
                ('mqtt_client_id_prefix', models.CharField(
                    default='ThaiTechZone',
                    max_length=50,
                    verbose_name='MQTT Client ID Prefix',
                    help_text='Prefix สำหรับ MQTT Client ID เช่น ThaiTechZone → ThaiTechZone_tti_board_001',
                )),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Device Configuration',
                'verbose_name_plural': 'Device Configurations',
            },
        ),
    ]
