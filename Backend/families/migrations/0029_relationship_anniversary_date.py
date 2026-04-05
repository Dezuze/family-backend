from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('families', '0028_familyhead_name_ml'),
    ]

    operations = [
        migrations.AddField(
            model_name='relationship',
            name='anniversary_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
