from django.contrib import admin
from django.urls import path, include
from . import views  # assuming your home view is in BrainBank/views.py

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # This routes the home page
    path('', include('courses.urls')),  # This includes your courses app URLs
]