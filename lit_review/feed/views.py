from itertools import chain

from django.contrib.auth.models import User
from django.db.models import Value, CharField
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from .forms import TicketCreationForm, ReviewCreationForm
from .models import Ticket, Review
from users.models import UserFollows

def get_viewable_reviews(user):
    followed_user_id = get_users_follower(user)

    followed_review = Review.objects.filter(
        Q(user__in=followed_user_id) | Q(user=user) | Q(ticket__user=user)).annotate(
        content_type=Value('REVIEW', CharField()))

    answered_review = followed_review.filter(
        Q(user=user) | Q(ticket__user=user)).annotate(
        ans=Value('T', CharField()))

    followed_review = followed_review.exclude(pk__in=answered_review)

    return chain(followed_review, answered_review)


def get_viewable_tickets(user):
    followed_user = get_users_follower(user)
    answered_ticket = Review.objects.filter(user=user).values('ticket')

    follow_ticket = Ticket.objects.filter(
        Q(user__in=followed_user) | Q(user=user)).annotate(
        content_type=Value('TICKET', CharField()))

    answered_ticket = follow_ticket.filter(
        Q(pk__in=answered_ticket)).annotate(
        ans=Value('T', CharField()))

    follow_ticket = follow_ticket.exclude(pk__in=answered_ticket)

    return chain(follow_ticket, answered_ticket)


def get_posted_reviews(users):
    return Review.objects.filter(user=users).annotate(
        ans=Value('T', CharField()), content_type=Value('REVIEW', CharField()))


def get_posted_tickets(users):
    tickets = Ticket.objects.filter(user=users).annotate(
        content_type=Value('TICKET', CharField()))
    return tickets


def get_users_follower(user):
    return User.objects.filter(pk__in=UserFollows.objects.filter(user=user).values("followed_user"))


def render_user_feed(request):
    reviews = get_viewable_reviews(request.user)
    tickets = get_viewable_tickets(request.user)

    posts = sorted(
        chain(reviews, tickets),
        key=lambda post: post.time_created,
        reverse=True
    )

    return render(request,
                  "feed/home.html",
                  context={"posts": posts})


def render_user_posts(request):
    reviews = get_posted_reviews(request.user.pk)
    tickets = get_posted_tickets(request.user)

    answered_tickets = tickets.filter(
        Q(pk__in=reviews.filter(ticket__user=request.user).values('ticket'))).annotate(
        ans=Value('T', CharField()))

    tickets = tickets.exclude(pk__in=answered_tickets)

    posts = sorted(
        chain(reviews, tickets, answered_tickets),
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
