# Vercel WSGI Application
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')

# This is the WSGI application for Vercel
app = get_wsgi_application()
