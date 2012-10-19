django-polymorphic-tree
=======================

This is a stand alone module, which provides:

  " A polymorphic structure to display content in a tree. "

In other words, this module provides a node tree, where each node can be a different model type.
This allows you to freely structure tree data. For example:

* Build a tree of a root node, category nodes, leaf nodes, each with custom fields.
* Build a todo list of projects, categories and items.
* Build a book of chapters, sections, and pages.

Origin
------

This module was extracted out of django-fluent-pages_ because it turned out to serve a generic purpose.
This was done during contract work at Leukeleu_ (also known for their involvement in django-fiber_).


Installation
============

First install the module, preferably in a virtual environment::

    pip install django-polymorphic-tree

Or install the current repository::

    pip install -e git+https://github.com/edoburu/django-polymorphic-tree.git#egg=django-polymorphic-tree

The main dependencies are django-mptt_ and django-polymorphic_,
which will be automatically installed.

Configuration
-------------

Next, create a project which uses the application::

    cd ..
    django-admin.py startproject demo

Add the following to ``settings.py``::

    INSTALLED_APPS += (
        'polymorphic_tree',
        'polymorphic',
        'mptt',
    )


Usage
-----

The main feature of this module is creating a tree of custom node types.
It boils down to creating a application with 2 files:

The ``models.py`` file should define the custom node type, and any fields it has::

    from django.db import models
    from django.utils.translation import ugettext_lazy as _
    from polymorphic_tree.models import PolymorphicMPTTModel, PolymorphicTreeForeignKey


    # A base model for the tree:

    class BaseTreeNode(PolymorphicMPTTModel):
        parent = PolymorphicTreeForeignKey('self', blank=True, null=True, related_name='children', verbose_name=_('parent'))
        title = models.CharField(_("Title"), max_length=200)

        class Meta:
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


The ``admin.py`` file should define the admin, both for the child nodes and parent::

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


The ``child_models`` attribute defines which admin interface is loaded for hte *edit* and *delete* page.
The list view is still rendered by the parent admin.


Todo
----

* Sphinx Documentation
* Unit tests
* Example app
* A final review of class names (hence the alpha version tag, but we will provide aliases for the old names)
* Getting the polymorphic-admin code merged upstream back into django-polymorphic_ (see `pull request #10 <https://github.com/chrisglass/django_polymorphic/pull/10>`_).


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
.. _django-polymorphic: https://github.com/chrisglass/django_polymorphic

