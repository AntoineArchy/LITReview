from django import forms
from django.forms import Textarea, TextInput
from main.forms import DEFAULT_TEXT_INPUT_ATTRS, DEFAULT_TEXT_AREA_ATTRS

from .models import Ticket, Review


class TicketCreationForm(forms.ModelForm):
    """
    Permet la création et l'édition de Ticket

    Requiert un titre et une description
    L'ajout d'une image est optionnel
    """
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']
        widgets = {
            "title": TextInput(
                attrs=DEFAULT_TEXT_INPUT_ATTRS),
            "description": Textarea(
                attrs=DEFAULT_TEXT_AREA_ATTRS
            )
        }


class ReviewCreationForm(forms.ModelForm):
    """
    Permet la création et l'édition de Review

    Requiert un titre, un corp de texte et une notation.
    """
    class Meta:
        model = Review
        fields = ['headline', 'body', 'rating']
        widgets = {
            "headline": TextInput(
                attrs=DEFAULT_TEXT_INPUT_ATTRS),
            "body": Textarea(
                attrs=DEFAULT_TEXT_AREA_ATTRS,)
        }
