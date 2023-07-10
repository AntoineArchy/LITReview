from django import forms
from django.forms import Textarea, TextInput
from main.forms import DEFAULT_TEXT_INPUT_ATTRS, DEFAULT_TEXT_AREA_ATTRS

from .models import Ticket, Review


class TicketCreationForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']
        widgets = {
            "title": TextInput(attrs={**DEFAULT_TEXT_INPUT_ATTRS}),
            "description": Textarea(
                attrs={**DEFAULT_TEXT_AREA_ATTRS}
            )
        }


class ReviewCreationForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['headline', 'body', 'rating']
        widgets = {
            "headline": TextInput(attrs={**DEFAULT_TEXT_INPUT_ATTRS}),
            "body": Textarea(
                attrs={**DEFAULT_TEXT_AREA_ATTRS},)
        }
