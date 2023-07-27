from __future__ import annotations

from itertools import chain
from typing import Iterable

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, QuerySet
from django.db.models import Value, CharField, BooleanField
from django.http import HttpRequest
from django.shortcuts import render, redirect

from users.views import get_user_followed
from .forms import TicketCreationForm, ReviewCreationForm
from .models import Ticket, Review


def get_users_viewable_reviews(user: User) -> Iterable:
    """
    Retourne un itérable de reviews visualisable par l'utilisateur

    Reçoit un objet utilisateur, récupère les utilisateurs suivis par l'utilisateur correspondant :
        Filtre les reviews pour récupérer toutes celles visualisables par l'utilisateur
        Annote celles pour lesquelles l'utilisateur a déjà répondu au ticket

    Retourne un itérable de l'intégralité des reviews visualisables par l'utilisateur.
    """
    followed_user_id = get_user_followed(user.pk)

    reviews_viewable_by_user = Review.objects.filter(
        Q(user__in=followed_user_id) | Q(user=user) | Q(ticket__user=user)).annotate(
        content_type=Value('REVIEW', CharField()))

    # On annote les reviews ayant un ticket déjà répondu par l'utilisateur pour ne pas afficher le bouton "répondre"
    reviews_answered_by_user = reviews_viewable_by_user.filter(
        Q(user=user) | Q(ticket__in=Review.objects.filter(
            user=user).values('ticket'))).annotate(
        answered=Value(True, BooleanField()))

    reviews_answerable_by_user = reviews_viewable_by_user.exclude(pk__in=reviews_answered_by_user)

    return chain(reviews_answerable_by_user, reviews_answered_by_user)


def get_users_viewable_tickets(user: User) -> Iterable:
    """
    Retourne un itérable de tickets visualisable par l'utilisateur

    Reçoit un objet utilisateur, récupère les utilisateurs suivis par l'utilisateur correspondant :
        Filtre les tickets pour récupérer tous ceux visualisables par l'utilisateur
        Annote ceux pour lesquelles l'utilisateur a déjà créé une review

    Retourne un itérable de l'intégralité des tickets visualisables par l'utilisateur.
    """
    followed_user_id = get_user_followed(user.pk)

    ticket_viewable_by_user = Ticket.objects.filter(
        Q(user__in=followed_user_id) | Q(user=user)).annotate(
        content_type=Value('TICKET', CharField()))

    # On annote les tickets auxquels l'utilisateur a déjà répondu pour ne pas afficher le bouton "répondre"
    tickets_answered_by_user = ticket_viewable_by_user.filter(
        Q(pk__in=Review.objects.filter(user=user).values('ticket'))).annotate(
        answered=Value(True, BooleanField()))

    tickets_answerable_by_user = ticket_viewable_by_user.exclude(pk__in=tickets_answered_by_user)

    return chain(tickets_answerable_by_user, tickets_answered_by_user)


@login_required
def render_user_feed(request: HttpRequest) -> HttpRequest:
    """
    Permet à un utilisateur de visualiser les contenus qu'il a créés sur LITReview

    Reçoit une requête par un utilisateur authentifié :
        Récupère les reviews visualisables par l'utilisateur,
        Récupère les tickets visualisables par l'utilisateur,
        Ordonnent les reviews et tickets par date de création

    Les reviews et tickets sont alors transmis au contexte lors de l'affichage du feed de l'utilisateur.
    """
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


def get_users_posted_reviews(user: User) -> QuerySet:
    """
    Retourne un itérable de reviews créées par l'utilisateur

    Reçoit un objet utilisateur :
    Retourne les reviews créée par l'utilisateur
    """
    return Review.objects.filter(user=user).annotate(
        content_type=Value('REVIEW', CharField()),
    )


def get_users_posted_tickets(user: User) -> QuerySet:
    """
    Retourne un itérable de tickets créés par l'utilisateur

    Reçoit un objet utilisateur :
    Retourne les tickets créés par l'utilisateur
    """
    return Ticket.objects.filter(user=user).annotate(
        content_type=Value('TICKET', CharField())
    )


@login_required
def render_user_posts(request: HttpRequest) -> HttpRequest:
    """
    Permet l'affichage des contenus créés par l'utilisateur

    Reçoit une requête par un utilisateur authentifié :
        Récupère les reviews créées par l'utilisateur,
        Récupère les tickets créés par l'utilisateur,
        Ordonnent les reviews et tickets par date de création

    Les reviews et tickets sont alors transmis au contexte lors de l'affichage du feed de l'utilisateur.
    """

    own_reviews = get_users_posted_reviews(request.user.pk)
    # L'intégralité des reviews crée par l'utilisateur concerne un ticket auquel il a répondu
    own_reviews = own_reviews.annotate(answered=Value(True, BooleanField()))

    own_tickets = get_users_posted_tickets(request.user)
    # L'utilisateur ne peut pas répondre à un ticket depuis la page de visualisation de son contenu créé
    own_tickets = own_tickets.annotate(answered=Value(True, BooleanField()))

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
def make_ticket(request: HttpRequest, instance: TicketCreationForm | None = None) -> Ticket | None:
    """
    Créer les objets tickets

    Reçoit une requête contenant un formulaire de création ou d'édition de ticket :
        S'il est valide, le ticket est retourné
        S'il est invalide, on retourne None
    """
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
def make_review(request: HttpRequest, ticket_id: int, instance: ReviewCreationForm | None = None) -> Review | None:
    """
    Créer les objets reviews

    Reçoit une requête contenant un formulaire de création ou d'édition de reviews :
        S'il est valide, la review est retournée
        S'il est invalide, on retourne None
    """
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
def post_create_new_ticket_request(request: HttpRequest) -> HttpRequest:
    """
    Reçoit une requête contenant un formulaire de création ou d'édition de ticket :
        Transmet la requête à la fonction permettant la vérification et la création de ticket
        Si le ticket est créé avec succès, on le sauvegarde en base

    L'utilisateur est alors redirigé vers la page principale
    """
    new_ticket = make_ticket(request)
    if new_ticket is not None:
        new_ticket.save()
    return redirect("main:homepage")


@login_required
def create_new_ticket_request(request: HttpRequest) -> HttpRequest:
    """
    Permet la création de nouveaux tickets

    Si la requête est POST, elle est transmise à la fonction appropriée.

    Instancie un formulaire de création de ticket,
    Transmet le formulaire au contexte lors de la visualisation de la page de création de contenus
    """
    if request.method == "POST":
        return post_create_new_ticket_request(request)
    ticket_form = TicketCreationForm()
    return render(request,
                  'feed/content_creation_page.html',
                  context={'ticket_form': ticket_form,
                           'user': request.user})


@login_required
def post_respond_to_ticket_request(request: HttpRequest, ticket_id: int) -> HttpRequest:
    """
    Reçoit une requête contenant un formulaire de création ou d'édition de review et un ticket_id :
        Transmet la requête à la fonction permettant la vérification et la création de review
        Si la review est créée avec succès, on la sauvegarde en base

    L'utilisateur est alors redirigé vers la page principale
    """
    new_review = make_review(request, ticket_id)
    if new_review is not None:
        new_review.save()
    return redirect("main:homepage")


@login_required
def respond_to_ticket_request(request: HttpRequest, ticket_id: int) -> HttpRequest:
    """
    Permet la création d'une review en réponse à un ticket.

    Reçoit une requête pouvant contenir un formulaire de création ou d'édition de reviews ainsi qu'un ticket_id :

    Contrôle l'existence du ticket :
        S'il n'existe pas l'utilisateur est redirigé vers la page de création de nouvelle review + nouveau ticket.
        S'il existe, il est récupéré depuis la bdd.

    Si la requête est POST, elle est transmise à la fonction appropriée qui s'occupera de la redirection utilisateur.

    Si la requête n'est pas une requête POST :
        Instancie un formulaire de création de review
        Le ticket correspondant au ticket_id et le formulaire sont alors transmis au contexte lors de l'affichage de
    la page de création de contenus.
    """

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
def post_create_new_review_request(request: HttpRequest) -> HttpRequest:
    """
    Reçoit une requête contenant un formulaire de création de ticket et un formulaire de création de review :

    Transmet le formulaire de création de ticket à la fonction appropriée :
        Si le ticket n'est pas valide, l'utilisateur reste sur la page de création de contenu

    Si le ticket est valide, le formulaire de création de review est transmis à la fonction appropriée :
        Si le formulaire de création de review n'est pas valide, l'utilisateur reste sur la page de création de contenu

    Si les deux formulaires sont valides, le ticket est sauvegardé en bdd, le ticket_id nouvellement crée est transmis
    à la nouvelle reviews avant sauvegarde en bdd.

    L'utilisateur est alors redirigé vers la page principale
    """
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
def create_new_review_request(request: HttpRequest) -> HttpRequest:
    """
    Permet la création simultanée d'un nouveau ticket et d'une nouvelle review en réponse à ce ticket.

    Si la requête est une requête POST, elle est transmise à la fonction appropriée.

    Instancie un formulaire de création de ticket
    Instancie un formulaire de création de review

    Transmet les formulaires au contexte lors de l'affichage de la page de création de contenus.
    """
    if request.method == "POST":
        return post_create_new_review_request(request)
    review_form = ReviewCreationForm()
    ticket_form = TicketCreationForm()
    return render(request,
                  'feed/content_creation_page.html',
                  context={'review_form': review_form,
                           'ticket_form': ticket_form})


@login_required
def delete_ticket(request: HttpRequest, ticket_id: int) -> HttpRequest:
    """
    Permet la suppression d'un ticket existant.

    Reçoit une requête et un ticket_id

    Contrôle l'existence du ticket :
        S'il existe, il est récupéré depuis la bdd.
    Contrôle le créateur du ticket :
        Si l'utilisateur est l'auteur du ticket, celui-ci est supprimé

    L'utilisateur est redirigé vers la page de visualisation du contenu créé
    """
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
def delete_review(request: HttpRequest, review_id: int) -> HttpRequest:
    """
    Permet la suppression d'une review existante.

    Reçoit une requête et un review_id

    Contrôle l'existence de la review :
        Si elle existe, elle est récupérée depuis la bdd.
    Contrôle le créateur de la review :
        Si l'utilisateur est l'auteur de la review, celle-ci est supprimée

    L'utilisateur est redirigé vers la page de visualisation du contenu créé
    """
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
def edit_ticket(request: HttpRequest, ticket_id: int):
    """
    Permet l'édition d'un ticket existant

    Reçoit une requête et un ticket_id :

    Contrôle l'existence du ticket :
        S'il n'existe pas l'utilisateur est redirigé vers la page de visualisation du contenu créé.
        S'il existe, il est récupéré depuis la bdd.

    Contrôle l'auteur du ticket :
        Si l'auteur n'est pas l'utilisateur authentifié, il est redirigé vers la page de visualisation du contenu créé.

    Si la requête est POST, elle est transmise à la fonction appropriée qui s'occupera de la mise à jour du ticket
    avant redirection de l'utilisateur vers la page de visualisation du contenu créé.

    Si la requête n'est pas une requête POST :
        Instancie un formulaire de création de ticket avec le ticket récupérée en tant qu'instance
        Le formulaire est alors transmis au contexte lors de l'affichage de la page de création de contenus.
    """
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
def edit_review(request: HttpRequest, review_id: int):
    """
        Permet l'édition d'une review existante

        Reçoit une requête et un review_id :

        Contrôle l'existence de la review :
            Si elle n'existe pas l'utilisateur est redirigé vers la page de visualisation du contenu créé.
            Si elle existe, elle est récupérée depuis la bdd.

        Contrôle l'auteur de la review :
            Si l'auteur n'est pas l'utilisateur authentifié, il est redirigé vers la page de visualisation du
            contenu créé.

        Si la requête est POST, elle est transmise à la fonction appropriée qui s'occupera de la mise à jour de la
        review avant redirection de l'utilisateur vers la page de visualisation du contenu créé.

        Si la requête n'est pas une requête POST :
            Instancie un formulaire de création de review
            Le formulaire est alors transmis au contexte lors de l'affichage de la page de création de contenus.
        """
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
