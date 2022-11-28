import os
import sys
from pathlib import Path

_parent_folder = Path(__file__).parent / ".."
sys.path.append(str(_parent_folder.resolve()))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings.vercel")

app = get_wsgi_application()
