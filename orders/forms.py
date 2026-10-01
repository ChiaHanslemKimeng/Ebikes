from django import forms
from orders.models import Order


class CheckoutForm(forms.ModelForm):
    accept_terms = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must accept the Terms and Conditions to proceed.'}
    )

    class Meta:
        model = Order
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'country',
            'city',
            'address',
            'postal_code',
            'delivery_notes',
            'payment_method',
            'other_payment_method',
            'card_number',
            'card_expiry',
            'card_cvv',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name', 'required': True}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address', 'required': True}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 000-0000', 'required': True}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country', 'required': True}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City', 'required': True}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street Address, Apartment, Suite', 'required': True}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code / ZIP', 'required': True}),
            'delivery_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Gate code, drop-off instructions, or timing preferences'}),
            'payment_method': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'other_payment_method': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'e.g. Venmo, PayPal, Fleet Purchase Order, Cash on Delivery'}),
            'card_number': forms.TextInput(attrs={'id': 'ccNumber', 'class': 'form-control form-control-sm font-monospace', 'placeholder': '4242 •••• •••• 4242', 'maxlength': '19'}),
            'card_expiry': forms.TextInput(attrs={'id': 'ccExpiry', 'class': 'form-control form-control-sm font-monospace', 'placeholder': 'MM / YY', 'maxlength': '7'}),
            'card_cvv': forms.PasswordInput(attrs={'id': 'ccCvv', 'class': 'form-control form-control-sm font-monospace', 'placeholder': 'CVC', 'maxlength': '4'}, render_value=True),
        }

