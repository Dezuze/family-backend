from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_post_is_kudumbayogam'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_auto_generated',
            field=models.BooleanField(default=False),
        ),
    ]
