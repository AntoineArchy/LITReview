from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, UsernameField, UserCreationForm

from main.forms import DEFAULT_TEXT_INPUT_ATTRS


class UserSearchInput(forms.Form):
    """
    Permet la recherche d'utilisateurs enregistrés dans la bdd.

    Requiert un nom d'utilisateur.
    """
    user_name = forms.CharField(max_length=100,
                                error_messages={'required': 'You need to enter a username to follow'},
                                widget=forms.TextInput(
                                    attrs=DEFAULT_TEXT_INPUT_ATTRS))


class UserAuthenticationForm(AuthenticationForm):
    """
    Permet l'authentification d'un utilisateur.

    Requiert un nom d'utilisateur et un mot de passe.
    """
    def __init__(self, *args, **kwargs):
        super(UserAuthenticationForm, self).__init__(*args, **kwargs)

    username = UsernameField(widget=forms.TextInput(
        attrs=DEFAULT_TEXT_INPUT_ATTRS))

    password = forms.CharField(max_length=100,
                               widget=forms.PasswordInput(
                                   attrs=DEFAULT_TEXT_INPUT_ATTRS))


class RegistrationForm(UserCreationForm):
    """
    Permet à un utilisateur de s'inscrire sur LITReview.


    Requiert un nom d'utilisateur, un mot de passe et une confirmation du mot de passe.
    """
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

    username = UsernameField(widget=forms.TextInput(
        attrs={
            **DEFAULT_TEXT_INPUT_ATTRS,
            "autofocus": True,
        }),
        help_text="Enter the desired username.",
    )

    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                **DEFAULT_TEXT_INPUT_ATTRS,
            }),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(
            attrs={
                **DEFAULT_TEXT_INPUT_ATTRS
            }),
        strip=False,
        help_text="Enter the same password as before, for verification.",
    )
