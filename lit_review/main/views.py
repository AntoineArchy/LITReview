from django.http import HttpResponseNotFound
from django.shortcuts import redirect, render
from django.template.loader import render_to_string


def homepage(request):
    if request.user.is_authenticated:
        return redirect("feed:home")
    return redirect("users:authentication_page")
