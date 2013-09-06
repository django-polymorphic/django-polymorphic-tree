Changes in version 0.8.10 (beta release)
-------------------------------------------

* Hide "add" icon when there is no permission.
* Fix Django 1.6 deprecation warnings for simplejson module.


Changes in version 0.8.9 (beta release)
-------------------------------------------

* Added workaround for large data sets, temporarily disabled pagination.
  NOTE: this issue needs to be looked at in more depth, and is a quick fix only.


Changes in version 0.8.8 (beta release)
-------------------------------------------

* Fix deprecation warning from django-polymorphic_.
* Fix Django 1.3 support by 0.8.7 (will only bump app requirements on major releases, e.g. 0.9).


Changes in version 0.8.7 (beta release)
---------------------------------------

* Fix Django 1.5 support in the templates
* Fix Django 1.6 support, use new ``django.conf.urls`` import path.
  Note you need to use django-polymorphic_ >= 0.5.1 as well with Django 1.6.


Changes in version 0.8.6 (beta release)
---------------------------------------

* Fixes for moving nodes in the admin:

 * Call ``model.save()`` so post-save updates are executed.
 * Update the preview URL in the "Actions" column.
 * Perform database updates in a single transaction.


Changes in version 0.8.5 (beta release)
---------------------------------------

* Depend on django-polymorphic_ 0.3.1, which contains our ``PolymorphicParentAdmin`` now.
* Depend on django-tag-parser_, the tag parsing utilities have been migrated to that app.
* Marked as beta release, as the API of the polymorphic admin is now finalized.


Changes in version 0.8.4 (alpha release)
----------------------------------------

* Fix list appearance in combination with django-grapelli
* Improve error messages on invalid movements


Changes in version 0.8.3 (alpha release)
----------------------------------------

* Fix row alignment in the admin interface
* Spelling and typoo fixes, print statement


Changes in version 0.8.2 (alpha release)
----------------------------------------

* **BIC:** Changed changed the dynamic model registration in ``PolymorphicParentAdmin``.

  Instead of ``get_child_model_classes()`` + ``get_admin_for_model()``
  there is a ``get_child_models()`` method that works like the static ``child_models`` registration.
  This also removes to need to provide a ``ModelAdmin`` instance somehow, only the class has to be provided.

* Fixed ``raw_id_fields`` for child admins.
* Fixed accidental late registration of models, fixes the "Save and Continue" button.
* Improved protection of custom subclass views.
* Generate ``django.mo`` files during ``setup.py sdist``.
* Added Dutch translation


Changes in version 0.8.1 (alpha release)
----------------------------------------

* Added ``type_label`` to ``NodeTypeChoiceForm``, for simple label switching.
* Added API's to support django-fluent-pages_, and other systems:

 * Allow the model.``can_have_children`` to be a property
 * Allow to override the error message in PolymorphicTreeForeignKey
 * Added ``can_preview_object()`` code in the admin, used in the actions column.

* Updated README examples


Changes in version 0.8.0 (alpha release)
----------------------------------------

First alpha release, extracted from django-fluent-pages_.

Simplified a lot of code to be tightly focused on the MPTT + Polymorphic code,
and not bother with a plugin registration system.


.. _django-fluent-pages: https://github.com/edoburu/django-fluent-pages
.. _django-polymorphic: https://github.com/chrisglass/django_polymorphic
.. _django-tag-parser: https://github.com/edoburu/django-tag-parser

