from itertools import chain

from django.db.models import Value, CharField
from django.shortcuts import render
from .form import TicketCreationForm
from .models import Ticket

# Create your views here.

def get_users_viewable_reviews(user):
    pass

def get_users_viewable_tickets(user):
    return Ticket.objects.all()


def user_feed(request):
    # reviews = get_users_viewable_reviews(request.user)
    # # returns queryset of reviews
    # reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    tickets = get_users_viewable_tickets(request.user)
    # returns queryset of tickets
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))

    # combine and sort the two types of posts
    posts = sorted(
        # chain(reviews, tickets),
        chain(tickets, tickets),
        key=lambda post: post.time_created,
        reverse=True
    )

    return render(request,
                  "feed/home.html",
                  context={"posts":posts})

def ticket_creation(request):
    form = TicketCreationForm()
    return render(request,
                  'feed/ticket_creation_page.html',
                  context={'form': form})
