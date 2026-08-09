from payments.models import DonationOption

DonationOption.objects.get_or_create(title='SUPPORTER', amount=500, purpose='Help us cover basic maintenance costs.', upi_id='merchant@upi', payee_name='Family Association', order=1)
DonationOption.objects.get_or_create(title='SPONSOR', amount=1500, purpose='Keep the platform running and secure.', upi_id='merchant@upi', payee_name='Family Association', order=2)
DonationOption.objects.get_or_create(title='BENEFACTOR', amount=5000, purpose='Support the development of new features.', upi_id='merchant@upi', payee_name='Family Association', order=3)
