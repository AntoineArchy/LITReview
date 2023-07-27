from django.http import HttpRequest
from django.shortcuts import redirect


def homepage(request: HttpRequest):
    """
    Est responsable de la redirection de base du projet : Si l'utilisateur est authentifié, il est redirigé sur
    son feed, sinon sur la page d'authentification
    """
    if request.user.is_authenticated:
        return redirect("feed:home")
    return redirect("users:authentication_page")
