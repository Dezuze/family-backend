from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import DonationOption

@admin.register(DonationOption)
class DonationOptionAdmin(ModelAdmin):
    list_display = ('title', 'amount', 'upi_id', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    search_fields = ('title', 'purpose', 'upi_id', 'payee_name')
    list_filter = ('is_active',)
