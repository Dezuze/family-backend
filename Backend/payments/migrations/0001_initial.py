from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('families', '0028_familyhead_name_ml'),
    ]

    operations = [
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('donor_name', models.CharField(max_length=120)),
                ('donor_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('donor_phone', models.CharField(blank=True, max_length=20, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(default='INR', max_length=10)),
                ('purpose', models.CharField(blank=True, max_length=200, null=True)),
                ('razorpay_order_id', models.CharField(max_length=80, unique=True)),
                ('razorpay_payment_id', models.CharField(blank=True, max_length=80, null=True, unique=True)),
                ('razorpay_signature', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('receipt_number', models.CharField(blank=True, max_length=40, null=True, unique=True)),
                ('receipt_pdf', models.FileField(blank=True, null=True, upload_to='receipts/')),
                ('receipt_token', models.CharField(blank=True, max_length=120, null=True, unique=True)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('donor_member', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='donations', to='families.familymember')),
                ('donor_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='donations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
