from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iot_dashboard', '0022_restore_push_on_filters'),
    ]

    operations = [
        migrations.AddField(
            model_name='n8npushsettings',
            name='push_all',
            field=models.BooleanField(
                default=True,
                verbose_name='⭐ ส่งพร้อมกันทุกค่า (Override)',
                help_text='ถ้าติ๊ก → ส่งทุก trigger โดยไม่สนใจ push_on_* แต่ละตัว | ถ้าไม่ติ๊ก → ใช้การตั้งค่า push_on_* ด้านล่าง',
            ),
        ),
    ]
