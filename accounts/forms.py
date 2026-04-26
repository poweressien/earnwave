from django import forms
from django.contrib.auth import authenticate
from .models import User, UserProfile

INPUT_CLASS = 'ew-form-control'
SELECT_CLASS = 'ew-form-control'


class SignupForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Create password', 'class': INPUT_CLASS})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password', 'class': INPUT_CLASS})
    )
    referral_code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Referral code (optional)', 'class': INPUT_CLASS})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First name', 'class': INPUT_CLASS}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last name', 'class': INPUT_CLASS}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email address', 'class': INPUT_CLASS}),
            'phone_number': forms.TextInput(attrs={'placeholder': '08012345678', 'class': INPUT_CLASS}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1', '')
        p2 = self.cleaned_data.get('password2', '')
        if p1 != p2:
            raise forms.ValidationError("Passwords don't match.")
        if len(p1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters.")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email address', 'class': INPUT_CLASS, 'autofocus': True})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': INPUT_CLASS})
    )
    remember_me = forms.BooleanField(required=False)

    def clean(self):
        email = self.cleaned_data.get('email', '').lower()
        password = self.cleaned_data.get('password', '')
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError('Invalid email or password. Please try again.')
            if not user.is_active:
                raise forms.ValidationError('This account has been deactivated.')
            if user.is_locked:
                raise forms.ValidationError('Account is locked due to suspicious activity. Please contact support.')
            self.user = user
        return self.cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'avatar', 'bio', 'date_of_birth', 'gender', 'state',
            'preferred_network', 'airtime_phone',
            'email_notifications', 'dark_mode'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 3, 'class': INPUT_CLASS,
                'placeholder': 'Tell us a bit about yourself...'
            }),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': INPUT_CLASS}),
            'gender': forms.Select(attrs={'class': SELECT_CLASS}),
            'state': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'e.g. Lagos'}),
            'preferred_network': forms.Select(attrs={'class': SELECT_CLASS}),
            'airtime_phone': forms.TextInput(attrs={
                'class': INPUT_CLASS, 'placeholder': '08012345678'
            }),
        }
