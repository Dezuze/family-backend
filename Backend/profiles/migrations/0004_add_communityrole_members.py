from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_communityrole'),
        ('families', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='communityrole',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='community_roles', to='families.familymember'),
        ),
    ]
