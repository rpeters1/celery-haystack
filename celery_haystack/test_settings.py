import os
from celery import Celery

app = Celery('celery_haystack')
app.config_from_object('django.conf:settings', namespace='CELERY')

DEBUG: bool = True

TEST_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), 'tests'))

INSTALLED_APPS: list[str] = [
    'haystack',
    'celery_haystack',
    'celery_haystack.tests',
]

DATABASES: dict[str, dict[str, str]] = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

SECRET_KEY: str = 'really-not-secret'

# Celery configurations for testing
CELERY_BROKER_URL = "memory://"
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_IGNORE_RESULT = True
CELERY_TASK_DEFAULT_QUEUE = "celery-haystack"
CELERY_TASK_DEFAULT_ROUTING_KEY = "celery-haystack"
CELERY_WORKER_LOG_LEVEL = "DEBUG"

# Haystack configuration for testing with Whoosh backend
HAYSTACK_CONNECTIONS: dict[str, dict[str, str]] = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(TEST_ROOT, 'whoosh_index'),
    }
}
HAYSTACK_SIGNAL_PROCESSOR = 'celery_haystack.signals.CelerySignalProcessor'
