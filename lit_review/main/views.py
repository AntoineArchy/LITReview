from django.shortcuts import redirect


def homepage(request):
    if request.user.is_authenticated:
        return redirect("feed:home")
    return redirect("users:authentication_page")