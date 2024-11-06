from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.apps import apps
from .conf import settings

from haystack import connections, connection_router
from haystack.exceptions import NotHandled as IndexNotFoundException

from celery import Task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class CeleryHaystackSignalHandler(Task):
    using: str = settings.CELERY_HAYSTACK_DEFAULT_ALIAS
    max_retries: int = settings.CELERY_HAYSTACK_MAX_RETRIES
    default_retry_delay: int = settings.CELERY_HAYSTACK_RETRY_DELAY

    def split_identifier(self, identifier: str, **kwargs) -> tuple[str | None, str | None]:
        """
        Break down the identifier representing the instance.

        Converts 'notes.note.23' into ('notes.note', 23).
        """
        bits = identifier.split('.')
        if len(bits) < 2:
            logger.error(f"Unable to parse object identifier '{identifier}'. Moving on...")
            return None, None

        pk = bits[-1]
        object_path = '.'.join(bits[:-1])
        return object_path, pk

    def get_model_class(self, object_path: str, **kwargs):
        """
        Fetch the model's class in a standardized way.
        """
        bits = object_path.split('.')
        app_name = '.'.join(bits[:-1])
        classname = bits[-1]
        model_class = apps.get_model(app_name, classname)

        if model_class is None:
            raise ImproperlyConfigured(f"Could not load model '{object_path}'.")
        return model_class

    def get_instance(self, model_class, pk, **kwargs):
        """
        Fetch the instance in a standardized way.
        """
        try:
            return model_class._default_manager.get(pk=pk)
        except model_class.DoesNotExist:
            logger.error(f"Couldn't load {model_class._meta.app_label.lower()}."
                         f"{model_class._meta.object_name.lower()}.{pk}. Somehow it went missing?")
        except model_class.MultipleObjectsReturned:
            logger.error(f"More than one object with pk {pk}. Oops?")
        return None

    def get_indexes(self, model_class, **kwargs):
        """
        Fetch the model's registered ``SearchIndex`` in a standardized way.
        """
        try:
            using_backends = connection_router.for_write(models=[model_class])
            for using in using_backends:
                index_holder = connections[using].get_unified_index()
                yield index_holder.get_index(model_class), using
        except IndexNotFoundException:
            raise ImproperlyConfigured(f"Couldn't find a SearchIndex for {model_class}.")

    def run(self, action: str, identifier: str, **kwargs) -> None:
        """
        Trigger the actual index handler depending on the
        given action ('update' or 'delete').
        """
        object_path, pk = self.split_identifier(identifier, **kwargs)
        if object_path is None or pk is None:
            msg = f"Couldn't handle object with identifier {identifier}"
            logger.error(msg)
            raise ValueError(msg)

        model_class = self.get_model_class(object_path, **kwargs)
        for current_index, using in self.get_indexes(model_class, **kwargs):
            current_index_name = f"{current_index.__class__.__module__}.{current_index.__class__.__name__}"

            if action == 'delete':
                try:
                    current_index.remove_object(identifier, using=using)
                except Exception as exc:
                    logger.exception(f"Error deleting '{identifier}' with {current_index_name}: {exc}")
                    self.retry(exc=exc)
                else:
                    logger.debug(f"Deleted '{identifier}' (with {current_index_name})")
            elif action == 'update':
                instance = self.get_instance(model_class, pk, **kwargs)
                if instance is None:
                    logger.debug(f"Failed updating '{identifier}' (with {current_index_name})")
                    raise ValueError(f"Couldn't load object '{identifier}'")

                try:
                    current_index.update_object(instance, using=using)
                except Exception as exc:
                    logger.exception(f"Error updating '{identifier}' with {current_index_name}: {exc}")
                    self.retry(exc=exc)
                else:
                    logger.debug(f"Updated '{identifier}' (with {current_index_name})")
            else:
                logger.error(f"Unrecognized action '{action}'. Moving on...")
                raise ValueError(f"Unrecognized action {action}")


class CeleryHaystackUpdateIndex(Task):
    """
    A celery task class to be used to call the update_index management
    command from Celery.
    """
    def run(self, apps: list[str] | None = None, **kwargs) -> None:
        defaults = {
            'batchsize': settings.CELERY_HAYSTACK_COMMAND_BATCH_SIZE,
            'age': settings.CELERY_HAYSTACK_COMMAND_AGE,
            'remove': settings.CELERY_HAYSTACK_COMMAND_REMOVE,
            'using': [settings.CELERY_HAYSTACK_DEFAULT_ALIAS],
            'workers': settings.CELERY_HAYSTACK_COMMAND_WORKERS,
            'verbosity': settings.CELERY_HAYSTACK_COMMAND_VERBOSITY,
        }
        defaults.update(kwargs)
        apps = apps or settings.CELERY_HAYSTACK_COMMAND_APPS

        logger.info("Starting update index")
        call_command('update_index', *apps, **defaults)
        logger.info("Finishing update index")
