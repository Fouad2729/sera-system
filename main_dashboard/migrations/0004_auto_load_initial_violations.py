from django.db import migrations
import os
from django.core.management import call_command

def load_data(apps, schema_editor):
    try:
        from django.conf import settings
        jpath = os.path.join(settings.BASE_DIR, 'main_dashboard', 'initial_violations.json')
        if os.path.exists(jpath):
            call_command('loaddata', jpath)
    except Exception:
        pass

class Migration(migrations.Migration):
    dependencies = [
        ('main_dashboard', '0003_remove_violation_description_remove_violation_title_and_more'),
    ]
    operations = [
        migrations.RunPython(load_data),
    ]
