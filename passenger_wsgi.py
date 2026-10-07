import os
import sys

# Ensure application directory is in Python path
sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from config.wsgi import application
