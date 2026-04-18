from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_add_communityrole_members'),
    ]

    operations = [
        migrations.AddField(
            model_name='communityrole',
            name='can_manage_all',
            field=models.BooleanField(default=False),
        ),
    ]
