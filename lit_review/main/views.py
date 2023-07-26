from django.http import HttpResponseNotFound
from django.shortcuts import redirect, render
from django.template.loader import render_to_string


def homepage(request):
    """
    Est responsable de la redirection de base du projet : Si l'utilisateur est authentifié, il est redirigé sur
    son feed, sinon sur la page d'authentification
    """
    if request.user.is_authenticated:
        return redirect("feed:home")
    return redirect("users:authentication_page")
