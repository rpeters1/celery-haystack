from django.db.models import signals
from django.dispatch import Signal
from haystack.signals import BaseSignalProcessor
from haystack.exceptions import NotHandled
from .utils import enqueue_task
from .indexes import CelerySearchIndex


class CelerySignalProcessor(BaseSignalProcessor):
    def setup(self) -> None:
        # Use `dispatch_uid` to prevent duplicate signal connections
        signals.post_save.connect(self.enqueue_save, dispatch_uid='celery_signal_processor_save')
        signals.post_delete.connect(self.enqueue_delete, dispatch_uid='celery_signal_processor_delete')

    def teardown(self) -> None:
        signals.post_save.disconnect(self.enqueue_save, dispatch_uid='celery_signal_processor_save')
        signals.post_delete.disconnect(self.enqueue_delete, dispatch_uid='celery_signal_processor_delete')

    def enqueue_save(self, sender: type, instance: object, **kwargs) -> None:
        self.enqueue('update', instance, sender, **kwargs)

    def enqueue_delete(self, sender: type, instance: object, **kwargs) -> None:
        self.enqueue('delete', instance, sender, **kwargs)

    def enqueue(self, action: str, instance: object, sender: type, **kwargs) -> None:
        """
        Enqueue a task for updating or deleting the search index based on the action.

        Args:
            action (str): 'update' or 'delete' action.
            instance (object): The model instance triggering the signal.
            sender (type): The model class of the instance.
        """
        using_backends = self.connection_router.for_write(instance=instance)

        for using in using_backends:
            try:
                connection = self.connections[using]
                index = connection.get_unified_index().get_index(sender)
            except NotHandled:
                continue  # Skip this backend if model is not handled

            if isinstance(index, CelerySearchIndex):
                if action == 'update' and not index.should_update(instance):
                    continue
                enqueue_task(action, instance)
