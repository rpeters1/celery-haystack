===============
celery-haystack
===============

.. image:: https://secure.travis-ci.org/django-haystack/celery-haystack.png?branch=develop
    :alt: Build Status
    :target: http://travis-ci.org/django-haystack/celery-haystack

This Django app allows you to utilize Celery for automatically updating and
deleting objects in a Haystack_ search index.

Requirements
------------

* Python 3.11
* Django 4.2.5
* Haystack 2.X_
* Celery 5.3.0

You will also need to install a supported search engine for Haystack and a backend for Celery.

.. _Haystack: http://haystacksearch.org
.. _Celery: http://www.celeryproject.org

Installation
------------

Install the package via PyPI:

    pip install celery-haystack

Usage
-----

1. Add ``'celery_haystack'`` to the ``INSTALLED_APPS`` setting:

   .. code:: python

     INSTALLED_APPS = [
         # ..
         'celery_haystack',
     ]

2. Enable the celery-haystack signal processor in your settings:

   .. code:: python

    HAYSTACK_SIGNAL_PROCESSOR = 'celery_haystack.signals.CelerySignalProcessor'

3. Update your ``SearchIndex`` subclasses to inherit from
   ``celery_haystack.indexes.CelerySearchIndex`` and
   ``haystack.indexes.Indexable``:

   .. code:: python

     from haystack import indexes
     from celery_haystack.indexes import CelerySearchIndex
     from myapp.models import Note

     class NoteIndex(CelerySearchIndex, indexes.Indexable):
         text = indexes.CharField(document=True, model_attr='content')

         def get_model(self):
             return Note

4. Ensure your Celery instance is running and configured.

Thanks
------

This app builds upon Daniel Lindsley's queued_search_ app but uses Ask Solem Hoel's Celery_ for queuing.

.. _queued_search: https://github.com/toastdriven/queued_search/
.. _Celery: http://celeryproject.org/
.. _queues: http://code.google.com/p/queues/

Issues
------

Please use the `Github issue tracker`_ for any bug reports or feature requests.

.. _`Github issue tracker`: https://github.com/django-haystack/celery-haystack/issues
