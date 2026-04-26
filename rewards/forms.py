from django import forms

class RedemptionForm(forms.Form):
    NETWORK_CHOICES = [('MTN', 'MTN'), ('Airtel', 'Airtel'), ('Glo', 'Glo'), ('9mobile', '9mobile')]
    network = forms.ChoiceField(choices=NETWORK_CHOICES)
    phone_number = forms.CharField(max_length=15)
    amount = forms.IntegerField(min_value=10)
