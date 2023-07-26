from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Value, BooleanField
from django.shortcuts import render, redirect

from .forms import UserAuthenticationForm
from .forms import UserSearchInput, RegistrationForm
from .models import UserFollows


def get_user_followed(user_id):
    return User.objects.filter(pk__in=UserFollows.objects.filter(user=user_id).values("followed_user"))


def get_following_user(user_id):
    return User.objects.filter(pk__in=UserFollows.objects.filter(followed_user=user_id).values("user"))


def post_authentication_request(request):
    if request.method == 'POST':
        form = UserAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now connected as {username}")
        else:
            for err_key, msg in form.errors.items():
                messages.error(request, msg)
    return redirect("main:homepage")


def authentication_request(request):
    if request.method == 'POST':
        return post_authentication_request(request)
    authentication_form = UserAuthenticationForm()
    return render(request,
                  "users/authentication_page.html",
                  context={"authentication_form": authentication_form})


def post_user_registration_request(request):
    registration_form = RegistrationForm(request.POST)
    if registration_form.is_valid():
        user = registration_form.save()
        login(request, user)
        messages.info(request, f"You are now connected as {user.username}")
        return redirect("main:homepage")
    else:
        for err_key, msg in registration_form.errors.items():
            messages.error(request, msg)
    return render(request,
                  'users/forms_display/registration_form.html',
                  context={"registration_form": registration_form})


def user_registration_request(request):
    if request.method == 'POST':
        return post_user_registration_request(request)
    registration_form = RegistrationForm()
    return render(request,
                  'users/forms_display/registration_form.html',
                  context={"registration_form": registration_form})


@login_required
def logout_user(request):
    logout(request)
    messages.info(request, "You are now disconnected.")
    return redirect("main:homepage")


@login_required
def post_user_follow(request):
    search_user_input = UserSearchInput(request.POST)
    if search_user_input.is_valid():
        user_name = search_user_input.cleaned_data.get("user_name")
        try:
            followed_user = User.objects.get(username=user_name)
            user = request.user
            if user == followed_user:
                raise ValueError
            UserFollows(user=user, followed_user=followed_user).save()
            messages.error(request, f"You are now following {user_name}")

        except ObjectDoesNotExist:
            messages.error(request, f"{user_name} :Oops seems like this user doesn't exist.")
        except ValueError:
            messages.error(request, "Sorry, you can't follow yourself.")
        except IntegrityError:
            messages.warning(request, f"You are already following this user ({user_name}).")

    else:
        for err_key, msg in search_user_input.errors.items():
            messages.error(request, msg)
    return redirect('users:follow')


@login_required
def render_user_follow(request):
    if request.method == 'POST':
        return post_user_follow(request)
    search_user_input = UserSearchInput()

    followed_users = get_user_followed(request.user.pk)
    followed_users = followed_users.annotate(is_followed=Value(True, BooleanField()))

    following_users = get_following_user(request.user.pk)

    return render(request,
                  "users/follow_page.html",
                  context={"search_user_input": search_user_input,
                           "followed": followed_users,
                           "following": following_users})


@login_required
def unfollow_user(request, user_id):
    try:
        other_user = User.objects.get(pk=user_id)
    except ObjectDoesNotExist:
        messages.error(request, "Seems like this user doesn't exist.")
        return redirect('users:follow')

    user_follow = UserFollows.objects.filter(user=request.user, followed_user=other_user)
    if not user_follow:
        messages.error(request, "You can't unfollow a user you don't follow")
    else:
        user_follow.delete()
        messages.info(request, f"You no longer follow {other_user.username}")

    return redirect('users:follow')
