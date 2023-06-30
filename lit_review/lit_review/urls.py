from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('main.urls')),
    path('', include('users.urls')),
    path('', include('feed.urls')),
    path('admin/', admin.site.urls),
]
