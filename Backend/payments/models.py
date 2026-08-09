from django.db import models

class DonationOption(models.Model):
    title = models.CharField(max_length=255, help_text="e.g. SPONSOR")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount in INR")
    purpose = models.TextField(help_text="e.g. Help us cover basic maintenance costs.")
    upi_id = models.CharField(max_length=255, help_text="e.g. merchant@upi")
    payee_name = models.CharField(max_length=255, help_text="e.g. ABC Store")
    is_active = models.BooleanField(default=True, help_text="Uncheck to hide this option")
    order = models.IntegerField(default=0, help_text="Order in which it appears on the frontend")

    class Meta:
        ordering = ['order', 'amount']
        verbose_name = "Donation Option"
        verbose_name_plural = "Donation Options"

    def __str__(self):
        return f"{self.title} - Rs. {self.amount}"
