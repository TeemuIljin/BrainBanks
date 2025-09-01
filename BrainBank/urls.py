from django.contrib import admin
from django.urls import path, include
from courses.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Root path explicitly handled
    path('', include('courses.urls')),  # Include other courses URLs
]