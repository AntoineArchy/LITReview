from itertools import chain

from django.contrib.auth.models import User
from django.db.models import Value, CharField, BooleanField
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from .forms import TicketCreationForm, ReviewCreationForm
from .models import Ticket, Review
from users.models import UserFollows


def get_users_viewable_reviews(user):
    followed_user_id = get_users_follower(user)

    reviews_viewable_by_user = Review.objects.filter(
        Q(user__in=followed_user_id) | Q(user=user) | Q(ticket__user=user)).annotate(
        content_type=Value('REVIEW', CharField()))

    reviews_answered_by_user = reviews_viewable_by_user.filter(
        Q(user=user) | Q(ticket__in=Review.objects.filter(
            user=user).values('ticket'))).annotate(
        answered=Value(True, BooleanField()))

    reviews_answerable_by_user = reviews_viewable_by_user.exclude(pk__in=reviews_answered_by_user)

    return chain(reviews_answerable_by_user, reviews_answered_by_user)


def get_users_viewable_tickets(user):
    followed_user_id = get_users_follower(user)

    ticket_viewable_by_user = Ticket.objects.filter(
        Q(user__in=followed_user_id) | Q(user=user)).annotate(
        content_type=Value('TICKET', CharField()))

    tickets_answered_by_user = ticket_viewable_by_user.filter(
        Q(pk__in=Review.objects.filter(user=user).values('ticket'))).annotate(
        answered=Value(True, BooleanField()))

    tickets_answerable_by_user = ticket_viewable_by_user.exclude(pk__in=tickets_answered_by_user)

    return chain(tickets_answerable_by_user, tickets_answered_by_user)


def get_users_follower(user):
    return User.objects.filter(pk__in=UserFollows.objects.filter(user=user).values("followed_user"))


@login_required
def render_user_feed(request):
    reviews = get_users_viewable_reviews(request.user)
    tickets = get_users_viewable_tickets(request.user)

    posts = sorted(
        chain(reviews, tickets),
        key=lambda post: post.time_created,
        reverse=True
    )

    return render(request,
                  "feed/home.html",
                  context={"posts": posts})


def get_users_posted_reviews(users):
    return Review.objects.filter(user=users).annotate(
        content_type=Value('REVIEW', CharField()),
        answered=Value(True, BooleanField()),
    )


def get_users_posted_tickets(users):
    return Ticket.objects.filter(user=users).annotate(
        content_type=Value('TICKET', CharField()),
        answered=Value(True, BooleanField()),

    )


@login_required
def render_user_posts(request):
    own_reviews = get_users_posted_reviews(request.user.pk)
    own_tickets = get_users_posted_tickets(request.user)

    posts = sorted(
        chain(own_reviews, own_tickets),
        key=lambda post: post.time_created,
        reverse=True
    )
    return render(request,
                  "feed/home.html",
                  context={"posts": posts,
                           "edit": True})


@login_required
def make_ticket(request, instance=None):
    form = TicketCreationForm(request.POST, request.FILES, instance=instance)
    if form.is_valid():
        new_ticket = form.save(commit=False)
        new_ticket.user = request.user
        if instance is None:
            messages.info(request, "Your ticket has been successfully created")
        else:
            messages.info(request, "Your ticket has been successfully updated")
        return new_ticket

    else:
        for err_key, msg in form.errors.items():
            messages.error(request, msg)
    return None


@login_required
def make_review(request, ticket_id, instance=None):
    form = ReviewCreationForm(request.POST, instance=instance)
    if form.is_valid():
        new_review = form.save(commit=False)
        new_review.user = request.user
        new_review.ticket_id = ticket_id
        if instance is None:
            messages.info(request, "Your review has been successfully created")
        else:
            messages.info(request, "Your review has been successfully updated")
        return new_review
    else:
        for err_key, msg in form.errors.items():
            messages.error(request, msg)
    return None


@login_required
def post_create_new_ticket_request(request):
    new_ticket = make_ticket(request)
    if new_ticket is not None:
        new_ticket.save()
    return redirect("main:homepage")


@login_required
def create_new_ticket_request(request):
    if request.method == "POST":
        return post_create_new_ticket_request(request)
    ticket_form = TicketCreationForm()
    return render(request,
                  'feed/content_creation_page.html',
                  context={'ticket_form': ticket_form,
                           'user': request.user})


@login_required
def post_respond_to_ticket_request(request, ticket_id):
    new_review = make_review(request, ticket_id)
    if new_review is not None:
        new_review.save()
    return redirect("main:homepage")


@login_required
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


@login_required
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


@login_required
def create_new_review_request(request):
    if request.method == "POST":
        return post_create_new_review_request(request)
    review_form = ReviewCreationForm()
    ticket_form = TicketCreationForm()
    return render(request,
                  'feed/content_creation_page.html',
                  context={'review_form': review_form,
                           'ticket_form': ticket_form})


@login_required
def delete_ticket(request, ticket_id):
    try:
        ticket = Ticket.objects.get(pk=ticket_id)
    except ObjectDoesNotExist:
        messages.error(request, "You tried to delete a ticket who doesn't exist.")
        return redirect('feed:posts')

    if ticket.user == request.user:
        ticket.delete()
        messages.info(request, "Your ticket has been successfully removed")
    else:
        messages.error(request, "You tried to delete a ticket who's not yours.")
    return redirect('feed:posts')


@login_required
def delete_review(request, review_id):
    try:
        review = Review.objects.get(pk=review_id)
    except ObjectDoesNotExist:
        messages.error(request, "You tried to delete a review who doesn't exist.")
        return redirect('feed:posts')

    if review.user == request.user:
        review.delete()
        messages.error(request, "Your review has been successfully removed")

    else:
        messages.error(request, "You tried to delete a review who's not yours.")
    return redirect('feed:posts')


@login_required
def edit_ticket(request, ticket_id):
    try:
        ticket = Ticket.objects.get(pk=ticket_id)
    except ObjectDoesNotExist:
        messages.error(request, "You tried to edit a ticket who doesn't exist.")
        return redirect('feed:posts')

    if ticket.user != request.user:
        messages.error(request, "You cannot edit other people tickets")
        return redirect('feed:posts')

    if request.method == 'POST':
        updated_ticket = make_ticket(request, instance=ticket)
        if updated_ticket is not None:
            updated_ticket.save()
            return redirect('feed:posts')

    ticket_form = TicketCreationForm(instance=ticket)
    return render(request,
                  'feed/content_creation_page.html',
                  context={'ticket_form': ticket_form,
                           'user': request.user})


@login_required
def edit_review(request, review_id):
    try:
        review = Review.objects.get(pk=review_id)
    except ObjectDoesNotExist:
        messages.error(request, "You tried to edit a review who doesn't exist.")
        return redirect('feed:posts')

    if review.user != request.user:
        messages.error(request, "You cant edit other people reviews")
        return redirect('feed:posts')

    if request.method == 'POST':
        updated_review = make_review(request, ticket_id=review.ticket, instance=review)
        if updated_review is not None:
            updated_review.save()
            return redirect('feed:posts')

    review_form = ReviewCreationForm(instance=review)
    return render(request,
                  'feed/content_creation_page.html',
                  context={'review_form': review_form,
                           'ticket': review.ticket})
