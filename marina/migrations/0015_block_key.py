from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('marina', '0014_alter_boat_options_alter_customer_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='block',
            name='key',
            field=models.CharField(blank=True, help_text="Mapping key for SVG coordinates (e.g., 'A', 'B', 'C')", max_length=10, null=True),
        ),
    ]
