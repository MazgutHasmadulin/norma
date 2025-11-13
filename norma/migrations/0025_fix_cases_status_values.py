# Generated migration to fix old status values in Cases

from django.db import migrations


def fix_cases_status(apps, schema_editor):
    """Преобразуем старые русские значения статусов в технические ключи"""
    Cases = apps.get_model('norma', 'Cases')
    
    # Маппинг старых значений на новые
    status_mapping = {
        'Черновик': 'draft',
        'На ревью': 'on_review',
        'Актуальный': 'actual',
        'Требует доработки': 'correction_needed'
    }
    
    for old_value, new_value in status_mapping.items():
        Cases.objects.filter(status=old_value).update(status=new_value)
        print(f"Updated Cases: {old_value} -> {new_value}")


def reverse_fix(apps, schema_editor):
    """Обратное преобразование (если нужно откатить)"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('norma', '0024_alter_cases_status'),
    ]

    operations = [
        migrations.RunPython(fix_cases_status, reverse_fix),
    ]
