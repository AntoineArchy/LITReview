from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate


def authentication_request(request):
    if request.method == 'POST':
        return login_user(request)
    form = AuthenticationForm()
    return render(request,
                  "users/authentication_page.html",
                  context={"form": form})


def register_user(request):
    form = UserCreationForm(request.POST)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("users:registered_homepage")
    else:
        for msg in form.error_messages:
            print(form.error_messages[msg])
    return render(request,
                  'users/registration_form.html',
                  context={"form":form})


def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("users:registered_homepage")
            # else:
            #     return redirect("/")
        else:
            for msg in form.error_messages:
                print(form.error_messages[msg])
    return redirect("main:homepage")


def logout_user(request):
    logout(request)
    return redirect("main:homepage")


def registered_homepage(request):
    return render(request,
                  "users/registered_home.html")

