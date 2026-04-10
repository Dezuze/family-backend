from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('families', '0026_clean_duplicate_spouses'),
    ]

    operations = [
        migrations.AddField(
            model_name='familymember',
            name='committee_role',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
    ]
