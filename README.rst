django-polymorphic-tree
=======================

This is a stand alone module, which provides:

  " A polymorphic structure to display content in a tree. "

In other words, this module provides a node tree, where each node type can be a different model.
This allows you to structure your site tree as you see fit. For example:

* Build a tree of a root node, category nodes, leaf nodes, each with custom fields.

Origin
------

This module was extracted out of django-fluent-pages_ because it turned out to serve a generic purpose.
This was done during contact work at Leukeleu_ (also known for their involvement in django-fiber_).


Installation
============

First install the module, preferably in a virtual environment::

    pip install -e git+https://github.com/edoburu/django-polymorphic-tree.git#egg=django-polymorphic-tree

The main dependencies are django-mptt_ and django-polymorphic_,
which will be automatically installed.

Configuration
-------------

Next, create a project which uses the CMS::

    cd ..
    django-admin.py startproject demo

Add the following to ``settings.py``::

    INSTALLED_APPS += (
        'polymorphic_tree',
        'polymorphic',
        'mptt',
    )

The database can be created afterwards::

    ./manage.py syncdb
    ./manage.py runserver


Custom node types
-----------------

The main feature of this module is the support for custom node types.
It boils down to creating a package with 2 files:

The ``models.py`` file should define the custom node type, and any fields it has::

    from django.db import models
    from django.utils.translation import ugettext_lazy as _
    from fluent_pages.models import HtmlPage
    from mysite.settings import RST_TEMPLATE_CHOICES


    class CategoryNode(PolymorphicMPTTModel):
        """
        A page that renders RST code.
        """
        title = models.CharField(_("Title"), max_length=200)

        class Meta:
            verbose_name = _("Category node")
            verbose_name_plural = _("Category node")

A ``node_type_plugins.py`` file that defines the metadata, and additional methods (e.g. rendering)::

    from polymorphic_tree.extensions import NodeTypePlugin, node_type_pool
    from .models import CategoryNode


    @node_type_pool.register
    class CategoryNodePlugin(NodeTypePlugin):
        model = CategoryNode
        sort_priority = 10

        def render(self, request, categorynode):
            return 'demo'

Optionally, a ``model_admin`` can also be defined, to have custom field layouts or extra functionality in the *edit* or *delete* page.

Plugin configuration
~~~~~~~~~~~~~~~~~~~~

The plugin can define the following attributes:

* ``model`` - the model for the page type
* ``model_admin`` - the custom admin to use (must inherit from ``PageAdmin``)
* ``can_have_children`` - whether the node type allows to have child nodes.
* ``urls`` - a custom set of URL patterns for sub pages (either a module name, or ``patterns()`` result).
* ``sort_priority`` - a sorting order in the "add page" dialog.


Contributing
------------

This module is designed to be generic. In case there is anything you didn't like about it,
or think it's not flexible enough, please let us know. We'd love to improve it!

If you have any other valuable contribution, suggestion or idea,
please let us know as well because we will look into it.
Pull requests are welcome too. :-)


.. _Leukeleu: http://www.leukeleu.nl/
.. _django-fiber: https://github.com/ridethepony/django-fiber
.. _django-fluent-pages: https://github.com/edoburu/django-fluent-blogs
.. _django-mptt: https://github.com/django-mptt/django-mptt
.. _django-polymorphic: https://github.com/chrisglass/django_polymorphic

