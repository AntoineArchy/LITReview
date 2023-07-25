from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, UsernameField, UserCreationForm

from main.forms import DEFAULT_TEXT_INPUT_ATTRS


class UserSearchInput(forms.Form):
    user_name = forms.CharField(max_length=100,
                                widget=forms.TextInput(
                                    attrs=DEFAULT_TEXT_INPUT_ATTRS))


class UserAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserAuthenticationForm, self).__init__(*args, **kwargs)

    username = UsernameField(widget=forms.TextInput(
        attrs=DEFAULT_TEXT_INPUT_ATTRS))

    password = forms.CharField(max_length=100,
                               widget=forms.PasswordInput(
                                   attrs=DEFAULT_TEXT_INPUT_ATTRS))


class RegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

    username = UsernameField(widget=forms.TextInput(
        attrs={
            **DEFAULT_TEXT_INPUT_ATTRS,
            "autofocus": True,
        }))

    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                **DEFAULT_TEXT_INPUT_ATTRS,
                "autocomplete": "new-password",
            }),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password",
                   **DEFAULT_TEXT_INPUT_ATTRS}),
        strip=False,
        help_text="Enter the same password as before, for verification.",
    )
