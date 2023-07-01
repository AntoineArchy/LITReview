from itertools import chain

from django.db.models import Value, CharField
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from .form import TicketCreationForm, ReviewCreationForm
from .models import Ticket, Review


# Create your views here.

def get_users_viewable_reviews(user):
    return Review.objects.all()


def get_users_viewable_tickets(user):
    return Ticket.objects.all()


def get_users_own_reviews(user):
    return Review.objects.filter(user=user.pk)


def get_users_own_tickets(user):
    return Ticket.objects.filter(user=user.pk)


def render_user_feed(request):
    reviews = get_users_viewable_reviews(request.user)
    # # returns queryset of reviews
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    tickets = get_users_viewable_tickets(request.user)
    # returns queryset of tickets
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))

    # combine and sort the two types of posts
    posts = sorted(
        chain(reviews, tickets),
        key=lambda post: post.time_created,
        reverse=True
    )

    return render(request,
                  "feed/home.html",
                  context={"posts": posts})


def make_ticket(request):
    form = TicketCreationForm(request.POST)
    if form.is_valid():
        new_ticket = form.save(commit=False)
        new_ticket.user = request.user
        return new_ticket
    else:
        for err_key, msg in form.errors.items():
            messages.error(request, msg)
    return None


def make_review(request, ticket_id):
    form = ReviewCreationForm(request.POST)
    if form.is_valid():
        new_review = form.save(commit=False)
        new_review.user = request.user
        new_review.ticket_id = ticket_id
        return new_review
    else:
        for err_key, msg in form.errors.items():
            messages.error(request, msg)
    return None


def post_create_new_ticket_request(request):
    new_ticket = make_ticket(request)
    if new_ticket is not None:
        new_ticket.save()
    return redirect("/")


def create_new_ticket_request(request):
    if request.method == "POST":
        return post_create_new_ticket_request(request)
    ticket_form = TicketCreationForm()
    return render(request,
                  'feed/content_creation_page.html',
                  context={'ticket_form': ticket_form,
                           'user': request.user})


def post_respond_to_ticket_request(request, ticket_id):
    new_review = make_review(request, ticket_id)
    if new_review is not None:
        new_review.save()
    return redirect("main:homepage")


def respond_to_ticket_request(request, ticket_id):
    try:
        ticket = Ticket.objects.get(pk=ticket_id)
    except ObjectDoesNotExist:
        messages.error(request, "You tried to answer to a ticket who doesn't exist.")
        return redirect('feed:review_creation')

    if request.method == "POST":
        return post_respond_to_ticket_request(request, ticket_id)
    review_form = ReviewCreationForm()
    return render(request,
                  'feed/content_creation_page.html',
                  context={'review_form': review_form,
                           'ticket': ticket})


def post_create_new_review_request(request):
    new_ticket = make_ticket(request)
    if new_ticket is not None:
        new_review = make_review(request, new_ticket.pk)
        if new_review is not None:
            new_ticket.save()
            new_review.ticket_id = new_ticket.pk
            new_review.save()
        return redirect('main:homepage')
    review_form = ReviewCreationForm()
    ticket_form = TicketCreationForm()
    return render(request,
                  'feed/content_creation_page.html',
                  context={'review_form': review_form,
                           'ticket_form': ticket_form})


def create_new_review_request(request):
    if request.method == "POST":
        return post_create_new_review_request(request)
    review_form = ReviewCreationForm()
    ticket_form = TicketCreationForm()
    return render(request,
                  'feed/content_creation_page.html',
                  context={'review_form': review_form,
                           'ticket_form': ticket_form})


def see_user_posts_request(request):
    reviews = get_users_own_reviews(request.user)
    # # returns queryset of reviews
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    tickets = get_users_own_tickets(request.user)
    # returns queryset of tickets
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))

    # combine and sort the two types of posts
    posts = sorted(
        chain(reviews, tickets),
        key=lambda post: post.time_created,
        reverse=True
    )
    return render(request,
                  "feed/home.html",
                  context={"posts": posts})


# def see_user_posts_request(request):
#     if request.method == "POST":
#         return post_see_user_posts_request(request)
