from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages


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
