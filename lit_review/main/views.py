from itertools import chain

from django.db.models import CharField, Value
from django.shortcuts import render, redirect

from .models import Review, Ticket

def homepage(request):
    if request.user.is_authenticated:
        return redirect("users:registered_home")
    return redirect("users:authentication_page")