from django import forms
from django.forms import Textarea, CharField, TextInput, CheckboxSelectMultiple

from .models import Ticket, Review


class TicketCreationForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']
        widgets = {
            "title": TextInput(attrs={"style": "background-color: white; resize:None; border-radius: 5px;"}),
            "description": Textarea(
                attrs={"style": "background-color: white; resize:None; border-radius: 5px; min-height:10rem",
                       "class": "materialize-textarea"}
            )
        }


class ReviewCreationForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['headline', 'body', 'rating']
        widgets = {
            "headline": TextInput(attrs={"style": "background-color: white; resize:None; border-radius: 5px;"}),
            "body": Textarea(
                attrs={"style": "background-color: white; resize:None; border-radius: 5px; min-height:10rem",
                       "class": "materialize-textarea"}),
        }
