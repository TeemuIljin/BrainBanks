from django.contrib import admin
from django.urls import path, include
from . import views  # assuming your home view is in BrainBank/views.py

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),  # This routes the home page
    path('courses/', include('courses.urls')),  # This includes your courses app URLs

]