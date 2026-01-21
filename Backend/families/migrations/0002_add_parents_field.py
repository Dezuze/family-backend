from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('families', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='familymember',
            name='parents',
            field=models.ManyToManyField(blank=True, related_name='children', symmetrical=False, to='families.familymember'),
        ),
    ]
