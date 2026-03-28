from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('families', '0022_alter_familymember_relation_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='relationship',
            name='is_inferred',
            field=models.BooleanField(default=False),
        ),
    ]
