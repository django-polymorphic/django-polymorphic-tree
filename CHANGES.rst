Changes in 1.5.1 (2020-01-04)
-----------------------------

* Fixed Django 3.0 compatibility by removing ``django.utils.six`` dependency.


Changes in 1.5 (2018-01-22)
---------------------------

* Added Django 2.0 support.
* Added ``base_manager_name`` setting in model ``Meta`` options, like django-polymorphic_ 2.0 does.
* Fixed crash in ``get_child_types()`` when ``can_have_children`` is ``False``.
* Fixed child type validation, this now happens before the database saves.
* Fixed spelling grapelli -> grappelli
* Dropped Django 1.8 support.


Changes in 1.4.2 (2017-11-22)
-----------------------------

* Fixed compatibility with recent django-polymorphic_ releases.
* Dropped support for unmaintained Django versions: 1.6, 1.7, 1.9
  (this should have warranted a 1.5 release, but it was accidentally slipped in).


Changes in 1.4.1 (2017-08-01)
-----------------------------

* Fixed inheriting ``PolymorphicMPTTModel`` in an abstract model.
* Fixed ``PolymorphicMPTTQuerySet.as_manager()`` usage to return the proper manager.


Changes in 1.4 (2017-02-18)
---------------------------

* Add ability to restrict children, via ``child_types`` list on the model.
  The value can be ``["self", "app.Model", "Model", Model]``.
* Added ability to set ``can_be_root`` to enforce using a node as child.
* Add ``validate_move_to()`` method to perform extra checks on moving children.
* Fix support for UUID fields as primary key.
* **Security notice:** fixed missing permission check on moving nodes, all staff members could move nodes.


Changes in 1.3.1 (2016-11-29)
-----------------------------

* Add Spanish (Argentina) language
* Fix rendering of empty list items on Django 1.9+ that have non-existing attributes/objects.
* Enforcing django-polymorphic_ >= 1.0.1 for Django 1.10.1 compatibility.
  (the previous version already required django-polymorphic_ 1.0)


Changes in 1.3
--------------

* Added Django 1.10 support
* Added convenient `get_closest_ancestor_of_type()` and `get_ancestors_of_type()` methods
* Support proxy model filtering by django-polymorphic_ 1.0
* Dropped Django 1.5 support / django-mptt 0.6 support.

.. note:: As of Django 1.10 managers of abstract classes are also inherited.
          Hence, the need to override ``_default_manager`` is removed.
          Use ``objects = YourPolymorphicMPTTManager()`` to override the manager now.

          Make sure django-polymorphic_ 1.0 is installed for Django 1.10 projects.


Changes in 1.2.5
----------------

* Fix grappelli theme appearance for admin list.


Changes in 1.2.4
----------------

* Fix ``admin/polymorphic_tree/object_history.html`` template typoo.


Changes in 1.2.3
----------------

* Fix tree list appearance for Django 1.8 and below (classic theme).


Changes in 1.2.2
----------------

* Fix tree list appearance for Django 1.9 and flat theme.


Changes in 1.2.1
----------------

* Fix breadcrumbs in Django 1.7+, displaying the ``AppConfig`` name.
* Fix breadcrumbs in ``object_history.html`` template.
  **NOTE:** This may require to redefine an ``admin/polymorphic_tree/object_history.html`` template
  when your project uses django-reversion_ or django-reversion-compare_.


Changes in 1.2
--------------

* Fix compatibility with Django 1.9.
* Fix support for MPTT ``get_previous_sibling()`` / ``get_next_sibling()``.
* Fix compatibility with django-polymorphic_ 0.8 final


Changes in 1.1.2
----------------

* Fix compatibility with upcoming django-polymorphic_ 0.8


Changes in 1.1.1
----------------

* Fixed URL resolving for for multi admin sites.
* Fixed URL breadcrumbs for delete page, visible when using non-standard delete URLs (e.g. django-parler_'s delete translation page).
* Fixed showing ``DateTimeField`` in local time.
* Enforcing at least django-polymorphic_ 0.7.1 for Django 1.8 compatibility.


Changes in version 1.1
----------------------

* Added Django 1.8 compatibility
* Added django-mptt 0.7 support
* Fixed Python 3 issue in the admin code
* Fixed attempting to import south in Django 1.7/1.8 environments
* Fixed default MPTT model ordering, using tree_id, lft now
* Test ``polymorphic.__version__`` to determine the api of ``get_child_type_choice()``.


Changes in version 1.0.1
------------------------

* Fixed Django 1.7 deprecation warnings
* Fix support for future 0.14, which removed ``future.utils.six``.


Changes in version 1.0
----------------------

* Added Python 3 support
* Added Django 1.7 support


Changes in version 0.9
----------------------

* Upgraded jqTree to latest version, and converted to a Git submodule
* Fix Django 1.6 transaction support
* Fix object ``.save()`` calls when moving items in the tree.
  There is no need to refetch the object, so the object ``.save()`` method can detect changes in it's parent.


Changes in version 0.8.11 (beta release)
-------------------------------------------

* Fix breadcrumbs, used `title`` attribute instead of ``__unicode__()``.


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

* Fix list appearance in combination with django-grappelli
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
.. _django-parler: https://github.com/edoburu/django-parler
.. _django-polymorphic: https://github.com/django-polymorphic/django-polymorphic
.. _django-reversion: https://github.com/etianen/django-reversion
.. _django-reversion-compare: https://github.com/jedie/django-reversion-compare
.. _django-tag-parser: https://github.com/edoburu/django-tag-parser

