from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('families', '0029_relationship_anniversary_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='familymember',
            name='committee_role',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
        migrations.AddField(
            model_name='familymember',
            name='wedding_anniversary',
            field=models.DateField(blank=True, null=True),
        ),
    ]
