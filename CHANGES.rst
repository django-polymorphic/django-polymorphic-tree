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

