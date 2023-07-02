from itertools import chain

from django.db.models import Value, CharField
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from .forms import TicketCreationForm, ReviewCreationForm
from .models import Ticket, Review
from users.models import UserFollows


# Create your views here.

def get_users_viewable_reviews(user):
    followed_user_id =  UserFollows.objects.filter(user=user).values("followed_user")


    answered_tickets = get_answered_ticket(user)
    answered_review = Review.objects.filter(ticket__in=answered_tickets, pk__in=followed_user_id)
    answered_review = answered_review.annotate(ans=Value('T', CharField()), content_type=Value('REVIEW', CharField()))#TODO Mark true for user own review

    viewable_review = Review.objects.filter(Q(user__in=followed_user_id) | Q(user=user)).exclude(pk__in=answered_review)
    viewable_review = viewable_review.annotate(content_type=Value('REVIEW', CharField()))

    reviews = chain(answered_review, viewable_review)

    return reviews


def get_users_viewable_tickets(user):
    followed_user_id =  UserFollows.objects.filter(user=user).values("followed_user")

    answered_tickets = get_answered_ticket(user)
    answered_tickets = answered_tickets.annotate(ans=Value('T', CharField()), content_type=Value('TICKET', CharField()))


    user_follow_ticket = Ticket.objects.filter(Q(user__in=followed_user_id) | Q(user=user)).exclude(pk__in=answered_tickets)
    user_follow_ticket = user_follow_ticket.annotate(content_type=Value('TICKET', CharField()))

    tickets = chain(answered_tickets, user_follow_ticket)

    return tickets

def get_answered_ticket(user):
    review_from_user = get_users_own_reviews(user).values('ticket')
    ticket_ans = Ticket.objects.filter(pk__in=review_from_user)
    return ticket_ans

def get_users_own_reviews(user):
    return Review.objects.filter(user=user.pk)


def get_users_own_tickets(user):
    return Ticket.objects.filter(user=user.pk)


def render_user_feed(request):
    reviews = get_users_viewable_reviews(request.user)
    # # returns queryset of reviews
    # reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    tickets = get_users_viewable_tickets(request.user)
    # tickets = tickets.annotate(content_type=Value('TICKET', CharField()))

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


def render_user_posts(request):
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

