from django.core.exceptions import ImproperlyConfigured
from importlib import import_module
from django.db import transaction
from haystack.utils import get_identifier
from .conf import settings


def get_update_task(task_path: str | None = None):
    """
    Imports and returns the Celery task class specified by task_path.

    Args:
        task_path (str | None): The full path of the task to be imported.

    Raises:
        ImproperlyConfigured: If the specified task cannot be imported.

    Returns:
        A Celery Task class instance.
    """
    import_path = task_path or settings.CELERY_HAYSTACK_DEFAULT_TASK
    module, attr = import_path.rsplit('.', 1)
    try:
        mod = import_module(module)
    except ImportError as e:
        raise ImproperlyConfigured(f'Error importing module {module}: "{e}"')
    try:
        Task = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured(f'Module "{module}" does not define a "{attr}" class.')
    return Task()


def enqueue_task(action: str, instance, **kwargs):
    """
    Enqueues a task for the given action and model instance.

    Args:
        action (str): The action to be performed (e.g., 'update' or 'delete').
        instance: The model instance associated with the action.
    """
    identifier = get_identifier(instance)
    options = {}
    if settings.CELERY_HAYSTACK_QUEUE:
        options['queue'] = settings.CELERY_HAYSTACK_QUEUE
    if settings.CELERY_HAYSTACK_COUNTDOWN:
        options['countdown'] = settings.CELERY_HAYSTACK_COUNTDOWN

    task = get_update_task()
    task_func = lambda: task.apply_async((action, identifier), kwargs, **options)

    # Use Django's on_commit hook to ensure task is queued only after transaction is committed
    if hasattr(transaction, 'on_commit'):
        transaction.on_commit(task_func)
    else:
        task_func()
