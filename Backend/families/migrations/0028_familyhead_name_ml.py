from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("families", "0027_familymember_name_ml"),
    ]

    operations = [
        migrations.AddField(
            model_name="familyhead",
            name="name_ml",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
