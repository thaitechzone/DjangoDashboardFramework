from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iot_dashboard', '0023_add_push_all_to_n8npushsettings'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='n8npushsettings',
            name='push_all',
        ),
    ]
