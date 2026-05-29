from django.db import migrations

def seed_tenants(apps, schema_editor):
    Tenant = apps.get_model('marina', 'Tenant')
    Tenant.objects.get_or_create(slug='ormos', defaults={
        'name': 'Ormos Marina',
        'owner_email': 'bernd@zaisers.myds.me',
        'is_active': True
    })
    Tenant.objects.get_or_create(slug='karlovasi', defaults={
        'name': 'Karlovasi Boatyard',
        'owner_email': 'bernd@zaisers.myds.me',
        'is_active': True
    })

def rollback_tenants(apps, schema_editor):
    Tenant = apps.get_model('marina', 'Tenant')
    Tenant.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('marina', '0038_tenant'),
    ]
    operations = [
        migrations.RunPython(seed_tenants, rollback_tenants),
    ]
