"""
WSGI config for lit_review project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lit_review.settings')

application = get_wsgi_application()
