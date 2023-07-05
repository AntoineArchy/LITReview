from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, UsernameField, UserCreationForm


class UserSearchInput(forms.Form):
    user_name = forms.CharField(max_length=100,
                                widget=forms.TextInput(
                                    attrs={"style": "background-color: white; resize:None; border-radius: 5px;"}))


class UserAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserAuthenticationForm, self).__init__(*args, **kwargs)

    username = UsernameField(widget=forms.TextInput(
        attrs={
            "style": "background-color: white; resize:None; border-radius: 5px;",
        }))

    password = forms.CharField(max_length=100,
                               widget=forms.PasswordInput(
                                   attrs={
                                       "style": "background-color: white; resize:None; border-radius: 5px;"}))


class RegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

    username = UsernameField(widget=forms.TextInput(
        attrs={
            "autofocus": True,
            "style": "background-color: white; resize:None; border-radius: 5px;",
            "class":"materialize-textarea",
            "label": "Usernaaaame"
        }))

    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password",
                   "style": "background-color: white; resize:None; border-radius: 5px;"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password",
                   "style": "background-color: white; resize:None; border-radius: 5px;"}),
        strip=False,
        help_text="Enter the same password as before, for verification.",
    )
