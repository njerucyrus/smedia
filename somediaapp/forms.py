from django import forms
from django.contrib.auth.models import User

from somediaapp.models import UserProfile


class TweetForm(forms.Form):
    product_name = forms.CharField(max_length=32, disabled=True)
    text = forms.CharField(max_length=140, widget=forms.Textarea(
        attrs={'id': 'text_id', 'placeholder': 'Advert broadcast tweet text'}
    ))


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", max_length=100, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', )

    # remove help text in the form
    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        for field_name in ['username', 'password', 'password2']:
            self.fields[field_name].help_text = None

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('business_name', )


class LoginForm(forms.Form):
    username = forms.CharField(max_length=32)
    password = forms.CharField(max_length=128, widget=forms.PasswordInput)


class ProductForm(forms.Form):
    product_name = forms.CharField(max_length=32)


