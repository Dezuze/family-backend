from django.db import migrations, models


def seed_default_roles(apps, schema_editor):
    CommunityRole = apps.get_model('profiles', 'CommunityRole')
    defaults = [
        ('Patron', 1),
        ('President', 2),
        ('Vice President', 3),
        ('Secretary', 4),
        ('Joint Secretary', 5),
        ('Treasurer', 6),
        ('Committee Member', 99),
    ]

    for name, priority in defaults:
        CommunityRole.objects.get_or_create(
            name=name,
            defaults={
                'priority': priority,
                'is_active': True,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_alter_gallery_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunityRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, unique=True)),
                ('priority', models.PositiveSmallIntegerField(default=100)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('priority', 'name'),
            },
        ),
        migrations.RunPython(seed_default_roles, migrations.RunPython.noop),
    ]
