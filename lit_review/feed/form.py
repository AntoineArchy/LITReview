from django.forms import ModelForm

from .models import Ticket, Review


class TicketCreationForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']


class ReviewCreationForm(ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'headline', 'body']
