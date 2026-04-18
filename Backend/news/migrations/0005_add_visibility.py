from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0004_add_is_auto_generated'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='visibility',
            field=models.CharField(default='public', max_length=32),
        ),
    ]
