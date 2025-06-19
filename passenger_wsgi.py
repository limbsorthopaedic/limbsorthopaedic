import sys
import os

# Add your project path
sys.path.insert(0, "/home3/limbsort/limbs_orthopaedic")

os.environ["DJANGO_SETTINGS_MODULE"] = "limbs_orthopaedic.settings"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()