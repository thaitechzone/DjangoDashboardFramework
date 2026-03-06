from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iot_dashboard', '0015_add_provider_to_geminiaisettings'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='geminiaisettings',
            name='provider',
        ),
    ]
