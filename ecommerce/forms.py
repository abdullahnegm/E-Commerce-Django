from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from django.core.exceptions import ValidationError
from .models import Refund

PAYMENT_CHOICES = (
    ("S" , "Stripe"),
    ("P" , "Paypal"),
)

class CheckoutForm(forms.Form):
    shipping_address = forms.CharField()
    shipping_address2 = forms.CharField(required=False)
    shipping_country = CountryField(blank_label='select country').formfield(
        widget=CountrySelectWidget(attrs={
        "class":"custome-select d-block w-100 form-control"}))
    shipping_zip = forms.CharField()
    same_billing_address = forms.BooleanField(required=False)
    set_default_shipping = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(widget=forms.RadioSelect , choices=PAYMENT_CHOICES)

    # def clean_shipping_address(self , *args , **kwargs):
    #     shipping_address1 = self.cleaned_data.get("shipping_address")
    #     if not shipping_address1:
    #         raise forms.ValidationError('This shit cant be empty')
    #     return shipping_address1

class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))

class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={"rows":4}))
    email = forms.EmailField()