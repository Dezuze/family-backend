from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('families', '0027_familymember_committee_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='familyhead',
            name='name_ml',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='familymember',
            name='name_ml',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
