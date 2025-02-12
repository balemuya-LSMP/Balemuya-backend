# users/apps.py
import os
from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    path = os.path.join(os.path.dirname(__file__)) 