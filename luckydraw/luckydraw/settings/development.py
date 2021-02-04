from .base import *

DEBUG = True


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(os.path.join(BASE_DIR.parent, "db.sqlite3")),
    }
}