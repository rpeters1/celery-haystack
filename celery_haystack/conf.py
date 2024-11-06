# same as above pythong 3.11, django 4.2.5 , celery 5.3.0
from __future__ import annotations

from django.conf import settings  # noqa
from django.core.exceptions import ImproperlyConfigured
from haystack import constants
from haystack.management.commands import update_index as cmd
from appconf import AppConf


class CeleryHaystack(AppConf):
    # Default alias for the search backend
    DEFAULT_ALIAS: str | None = None
    # Delay before task execution (in seconds)
    COUNTDOWN: int = 0
    # Delay for retry after failure (in seconds)
    RETRY_DELAY: int = 5 * 60
    # Maximum number of retries for failed tasks
    MAX_RETRIES: int = 1
    # Default task to be used for CeleryHaystack
    DEFAULT_TASK: str = 'celery_haystack.tasks.CeleryHaystackSignalHandler'
    # Optional name of the Celery queue
    QUEUE: str | None = None
    # If the task should be handled with transaction safety
    TRANSACTION_SAFE: bool = True

    # Task-specific configurations
    COMMAND_BATCH_SIZE: int | None = None
    COMMAND_AGE: int | None = None
    COMMAND_REMOVE: bool = False
    COMMAND_WORKERS: int = 0
    COMMAND_APPS: list[str] = []
    COMMAND_VERBOSITY: int = 1

    def configure_default_alias(self, value: str | None) -> str | None:
        return value or getattr(constants, 'DEFAULT_ALIAS', None)

    def configure_command_batch_size(self, value: int | None) -> int | None:
        return value or getattr(cmd, 'DEFAULT_BATCH_SIZE', None)

    def configure_command_age(self, value: int | None) -> int | None:
        return value or getattr(cmd, 'DEFAULT_AGE', None)

    def configure(self) -> dict:
        data = {}
        for name, value in self.configured_data.items():
            if name in {'RETRY_DELAY', 'MAX_RETRIES', 'COMMAND_WORKERS', 'COMMAND_VERBOSITY'}:
                data[name] = int(value)
            else:
                data[name] = value
        return data


# Ensure that the Haystack signal processor setting is configured correctly
signal_processor = getattr(settings, 'HAYSTACK_SIGNAL_PROCESSOR', None)
if signal_processor is None:
    raise ImproperlyConfigured(
        "celery-haystack requires HAYSTACK_SIGNAL_PROCESSOR to be set in your Django settings. "
        "Please set it to 'celery_haystack.signals.CelerySignalProcessor' for compatibility with Haystack."
    )
