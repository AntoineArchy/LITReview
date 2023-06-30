# from django.contrib import admin
from django.urls import path, include
from . import views


app_name = "feed"

urlpatterns = [
    path("home/", views.user_feed, name="home"),
    path("new_ticket/", views.ticket_creation, name="ticket_creation"),
]
