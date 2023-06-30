from django.urls import path
from . import views


app_name = "users"

urlpatterns = [
    path("registration/", views.register_user, name="register_user"),
    path("authentication_page/", views.authentication_request, name="authentication_page"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
]


