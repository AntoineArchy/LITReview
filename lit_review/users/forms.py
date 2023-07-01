from django import forms


class UserSearchInput(forms.Form):
    user_name = forms.CharField(label="", max_length=100, )
