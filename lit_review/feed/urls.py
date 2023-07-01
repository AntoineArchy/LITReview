# from django.contrib import admin
from django.urls import path, include
from . import views


app_name = "feed"

urlpatterns = [
    path("home/", views.render_user_feed, name="home"),
    path("new_ticket/", views.create_new_ticket_request, name="ticket_creation"),
    path("new_review/", views.create_new_review_request, name="review_creation"),
    path("new_review/<int:ticket_id>", views.respond_to_ticket_request, name="review_creation"),
]
