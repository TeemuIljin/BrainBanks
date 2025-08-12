import os
from django.core.wsgi import get_wsgi_application

# Set default Django settings module for WSGI application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BrainBank.settings')

application = get_wsgi_application()
