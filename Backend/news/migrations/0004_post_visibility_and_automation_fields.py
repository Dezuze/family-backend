from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('families', '0029_relationship_anniversary_date'),
        ('news', '0003_post_is_kudumbayogam'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='generated_for_member',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='generated_news_posts', to='families.familymember'),
        ),
        migrations.AddField(
            model_name='post',
            name='generated_key',
            field=models.CharField(blank=True, max_length=120, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='post',
            name='generated_kind',
            field=models.CharField(blank=True, choices=[('birthday', 'Birthday'), ('death_anniversary', 'Death Anniversary'), ('marriage_anniversary', 'Marriage Anniversary')], max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='is_auto_generated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='post',
            name='visibility',
            field=models.CharField(choices=[('public', 'Public'), ('members', 'Members Only')], default='public', max_length=20),
        ),
    ]
