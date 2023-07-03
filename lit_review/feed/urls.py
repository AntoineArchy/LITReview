# from django.contrib import admin
from django.urls import path, include
from . import views


app_name = "feed"

urlpatterns = [
    path("home/", views.render_user_feed, name="home"),
    path("new_ticket/", views.create_new_ticket_request, name="ticket_creation"),
    path("new_review/", views.create_new_review_request, name="review_creation"),
    path("new_review/<int:ticket_id>", views.respond_to_ticket_request, name="review_creation"),
    path("posts/", views.render_user_posts, name="posts"),
    path("del_ticket/<int:ticket_id>", views.delete_ticket, name="delete_ticket"),
    path("del_review/<int:review_id>", views.delete_review, name="delete_review"),
    path("edit_ticket/<int:ticket_id>", views.edit_ticket, name="edit_ticket"),
    path("edit_review/<int:review_id>", views.edit_review,  name="edit_review"),
]
