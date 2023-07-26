from django.urls import path
from . import views


app_name = "users"

urlpatterns = [
    path("registration/", views.user_registration_request, name="register_user"),
    path("authentication_page/", views.authentication_request, name="authentication_page"),
    path("logout/", views.logout_user, name="logout"),
    path("follow/", views.render_user_follow, name="follow"),
    path("unfollow/<int:user_id>", views.unfollow_user, name="follow"),

]
