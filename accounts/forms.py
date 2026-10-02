from django import forms
from django.contrib.auth.models import User
from accounts.models import UserProfile


class UserRegistrationForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 000-0000'}),
        help_text='For order dispatch and delivery updates.'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter a secure password'}),
        help_text='At least 8 characters long.'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Re-enter your password'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email address already exists.')
        return email


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'city', 'postal_code', 'country', 'avatar']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 000-0000'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street Address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country / Region'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }


from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm


class StrictPasswordResetForm(PasswordResetForm):
    """
    Password reset form that strictly validates that the email is registered
    in the database before sending any reset link.
    """
    email = forms.EmailField(
        label="Email Address",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'name@example.com',
            'autocomplete': 'email',
            'required': True,
            'autofocus': True,
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        users = User.objects.filter(email__iexact=email, is_active=True)
        if not users.exists():
            raise forms.ValidationError(
                "No active account found with this email address. Please check your spelling or register a new account."
            )
        return email


class StyledSetPasswordForm(SetPasswordForm):
    """
    Styled SetPasswordForm with clean Bootstrap 5 form-control styling.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'new_password1' in self.fields:
            self.fields['new_password1'].widget.attrs.update({
                'class': 'form-control form-control-lg',
                'placeholder': 'Enter new password (min. 8 characters)',
                'autocomplete': 'new-password',
                'id': 'newPassword1Input',
            })
        if 'new_password2' in self.fields:
            self.fields['new_password2'].widget.attrs.update({
                'class': 'form-control form-control-lg',
                'placeholder': 'Re-enter new password to confirm',
                'autocomplete': 'new-password',
                'id': 'newPassword2Input',
            })
