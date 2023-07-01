from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Value, CharField
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import UserSearchInput
from .models import UserFollows

def get_user_followed(user_id):
    followed_querry = User.objects.filter(pk__in=UserFollows.objects.filter(user=user_id).values("followed_user"))
    return followed_querry

def get_following_user(user_id):
    my_follower =  User.objects.filter(pk__in=UserFollows.objects.filter(followed_user=user_id).values("user"))
    return my_follower

def post_authentication_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
        else:
            for err_key, msg in form.errors.items():
                messages.error(request, msg)
    return redirect("main:homepage")


def authentication_request(request):
    if request.method == 'POST':
        return post_authentication_request(request)
    form = AuthenticationForm()
    return render(request,
                  "users/authentication_page.html",
                  context={"form": form})


def post_user_registration_request(request):
    form = UserCreationForm(request.POST)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("main:homepage")
    else:
        for err_key, msg in form.errors.items():
            messages.error(request, msg)
    return render(request,
                  'forms/users/registration_form.html',
                  context={"form": form})


def user_registration_request(request):
    if request.method == 'POST':
        return post_user_registration_request(request)
    form = UserCreationForm()
    return render(request,
                  'forms/users/registration_form.html',
                  context={"form": form})


def logout_user(request):
    logout(request)
    return redirect("main:homepage")

def post_user_follow(request):
    form = UserSearchInput(request.POST)
    if form.is_valid():
        user_name = form.cleaned_data.get("user_name")
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
            messages.error(request, f"Ahah, you can't follow yourself.")
    else:
        for err_key, msg in form.errors.items():
            messages.error(request, msg)
    return redirect('users:follow')


def render_user_follow(request):
    if request.method == 'POST':
        return post_user_follow(request)
    form = UserSearchInput()

    followed_users = get_user_followed(request.user.pk)
    followed_users = followed_users.annotate(content_type=Value('UNFLW', CharField()))
    following_users = get_following_user(request.user.pk)
    return render(request,
                  "users/follow.html",
                  context={"form": form,
                           "followed": followed_users,
                           "following": following_users})


def unfollow_user(request, user_id):
    current_user = request.user
    other_user = User.objects.get(pk=user_id)
    user_follow = UserFollows.objects.filter(user=current_user, followed_user=other_user)
    if not user_follow:
        messages.error(request, "You can't unfollow a user you don't follow")
    else:
        user_follow.delete()
    return redirect('users:follow')

