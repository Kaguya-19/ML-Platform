import os
import django
from celery import Celery
from django.conf import settings
 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MLPlatform.settings')
django.setup()
 
celery_app = Celery('MLPlatform')
celery_app.config_from_object('django.conf:settings')
celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)