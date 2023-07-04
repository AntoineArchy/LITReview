from django import forms


class UserSearchInput(forms.Form):
    user_name = forms.CharField(max_length=100,
                                widget=forms.TextInput(
                                    attrs={"style": "background-color: white; resize:None; border-radius: 5px;"}))

