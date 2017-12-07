.. image:: https://img.shields.io/travis/django-polymorphic/django-polymorphic-tree/master.svg?branch=master
    :target: http://travis-ci.org/django-polymorphic/django-polymorphic-tree
.. image:: https://img.shields.io/pypi/v/django-polymorphic-tree.svg
    :target: https://pypi.python.org/pypi/django-polymorphic-tree/
.. image:: https://img.shields.io/badge/wheel-yes-green.svg
    :target: https://pypi.python.org/pypi/django-polymorphic-tree/
.. image:: https://img.shields.io/pypi/l/django-polymorphic-tree.svg
    :target: https://pypi.python.org/pypi/django-polymorphic-tree/
.. image:: https://img.shields.io/codecov/c/github/django-polymorphic/django-polymorphic-tree/master.svg
    :target: https://codecov.io/github/django-polymorphic/django-polymorphic-tree?branch=master

django-polymorphic-tree
=======================

This package combines django-mptt_ with django-polymorphic_.
You can write Django models that form a tree structure where each node can be a different model type.

Example uses:

* Build a tree of organisation and company types (e.g. ``Partner``, ``Reseller``, ``Group`` and ``Customer``)
* Build a tree of a root node, category nodes, leaf nodes, each with custom fields.
* Build a todo list of projects, categories and items.
* Build a book of chapters, sections, and pages.

Origin
------

This code was created in django-fluent-pages_, and extracted to become a separate package.
This was done during contract work at Leukeleu_ (known for django-fiber_).


Installation
============

First install the module, preferably in a virtual environment::

    pip install django-polymorphic-tree

Or install the current repository::

    pip install -e git+https://github.com/django-polymorphic/django-polymorphic-tree.git#egg=django-polymorphic-tree

The main dependencies are django-mptt_ and django-polymorphic_,
which will be automatically installed.

Configuration
-------------

Next, create a project which uses the application::

    cd ..
    django-admin.py startproject demo

Add the following to ``settings.py``:

.. code:: python

    INSTALLED_APPS += (
        'polymorphic_tree',
        'polymorphic',
        'mptt',
    )


Usage
-----

The main feature of this module is creating a tree of custom node types.
It boils down to creating a application with 2 files:

The ``models.py`` file should define the custom node type, and any fields it has:

.. code:: python

    from django.db import models
    from django.utils.translation import ugettext_lazy as _
    from polymorphic_tree.models import PolymorphicMPTTModel, PolymorphicTreeForeignKey


    # A base model for the tree:

    class BaseTreeNode(PolymorphicMPTTModel):
        parent = PolymorphicTreeForeignKey('self', blank=True, null=True, related_name='children', verbose_name=_('parent'))
        title = models.CharField(_("Title"), max_length=200)

        class Meta(PolymorphicMPTTModel.Meta):
            verbose_name = _("Tree node")
            verbose_name_plural = _("Tree nodes")


    # Create 3 derived models for the tree nodes:

    class CategoryNode(BaseTreeNode):
        opening_title = models.CharField(_("Opening title"), max_length=200)
        opening_image = models.ImageField(_("Opening image"), upload_to='images')

        class Meta:
            verbose_name = _("Category node")
            verbose_name_plural = _("Category nodes")


    class TextNode(BaseTreeNode):
        extra_text = models.TextField()

        # Extra settings:
        can_have_children = False

        class Meta:
            verbose_name = _("Text node")
            verbose_name_plural = _("Text nodes")


    class ImageNode(BaseTreeNode):
        image = models.ImageField(_("Image"), upload_to='images')

        class Meta:
            verbose_name = _("Image node")
            verbose_name_plural = _("Image nodes")


The ``admin.py`` file should define the admin, both for the child nodes and parent:

.. code:: python

    from django.contrib import admin
    from django.utils.translation import ugettext_lazy as _
    from polymorphic_tree.admin import PolymorphicMPTTParentModelAdmin, PolymorphicMPTTChildModelAdmin
    from . import models


    # The common admin functionality for all derived models:

    class BaseChildAdmin(PolymorphicMPTTChildModelAdmin):
        GENERAL_FIELDSET = (None, {
            'fields': ('parent', 'title'),
        })

        base_model = models.BaseTreeNode
        base_fieldsets = (
            GENERAL_FIELDSET,
        )


    # Optionally some custom admin code

    class TextNodeAdmin(BaseChildAdmin):
        pass


    # Create the parent admin that combines it all:

    class TreeNodeParentAdmin(PolymorphicMPTTParentModelAdmin):
        base_model = models.BaseTreeNode
        child_models = (
            (models.CategoryNode, BaseChildAdmin),
            (models.TextNode, TextNodeAdmin),  # custom admin allows custom edit/delete view.
            (models.ImageNode, BaseChildAdmin),
        )

        list_display = ('title', 'actions_column',)

        class Media:
            css = {
                'all': ('admin/treenode/admin.css',)
            }


    admin.site.register(models.BaseTreeNode, TreeNodeParentAdmin)


The ``child_models`` attribute defines which admin interface is loaded for the *edit* and *delete* page.
The list view is still rendered by the parent admin.


Tests
-----

To run the included test suite, execute::

    ./runtests.py

To test support for multiple Python and Django versions, you need to follow steps below:

* install project requirements in virtual environment
* install python 2.7, 3.4, 3.5, 3.6 python versions through pyenv (See pyenv (Linux) or Homebrew (Mac OS X).)
* create .python-version file and add full list of installed versions with which project have to be tested, example::

    2.6.9
    2.7.13
    3.4.5
    3.5.2
    3.6.0
* run tox from the repository root::

    pip install tox
    tox

Python 2.7, 3.4, 3.5 and 3.6 and django 1.8, 1.10 and 1.11 are the currently supported versions.

Todo
----

* Sphinx Documentation


Contributing
------------

This module is designed to be generic. In case there is anything you didn't like about it,
or think it's not flexible enough, please let us know. We'd love to improve it!

If you have any other valuable contribution, suggestion or idea,
please let us know as well because we will look into it.
Pull requests are welcome too. :-)


.. _Leukeleu: http://www.leukeleu.nl/
.. _django-fiber: https://github.com/ridethepony/django-fiber
.. _django-fluent-pages: https://github.com/edoburu/django-fluent-pages
.. _django-mptt: https://github.com/django-mptt/django-mptt
.. _django-polymorphic: https://github.com/django-polymorphic/django-polymorphic

