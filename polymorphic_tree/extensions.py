"""
Special classes to extend the module; e.g. node type plugins.

The API uses a registration system.
While plugins can be easily detected via ``__subclasses__()``, the register approach is less magic and more explicit.
Having to do an explicit register ensures future compatibility with other API's such as django-reversion.
"""
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.db import DatabaseError
from django.utils.importlib import import_module
from polymorphic_tree.models import PolymorphicMPTTModel
from threading import Lock

__all__ = (
    'NodeTypePlugin', 'NodeTypeAlreadyRegistered', 'NodeTypeNotFound', 'NodeTypePool', 'node_type_pool'
)



class NodeTypePlugin(object):
    """
    The base class for a node type plugin.

    It combines the model, modeladmin and additional metadata of the node type.
    This is also the extension point to implement features such as rendering per node type.

    To create a new plugin, derive from this class and call :func:`plugin_pool.register <NodeTypePool.register>` to enable it.
    """
    __metaclass__ = forms.MediaDefiningClass

    # -- Settings to override:

    #: The model to use, must derive from :class:`polymorphic_tree.models.PolymorphicMPTTModel`.
    model = None

    #: The modeladmin instance to customize the screen.
    model_admin = None

    #: Whether the node type allows to have children.
    can_have_children = True

    #: The sorting priority for the add page.
    sort_priority = 100


    def __init__(self):
        self._type_id = None


    def __repr__(self):
        return '<{0} for {1} model>'.format(self.__class__.__name__, unicode(self.model.__name__).encode('ascii'))


    @property
    def verbose_name(self):
        """
        The title for the plugin, by default it reads the ``verbose_name`` of the model.
        """
        return self.model._meta.verbose_name


    @property
    def type_name(self):
        """
        Return the classname of the model, this is mainly provided for templates.
        """
        return self.model.__name__


    @property
    def type_id(self):
        """
        Shortcut to retrieving the ContentType id of the model.
        """
        if self._type_id is None:
            try:
                self._type_id = ContentType.objects.get_for_model(self.model).id
            except DatabaseError as e:
                raise DatabaseError("Unable to fetch ContentType object, is a plugin being registered before the initial syncdb? (original error: {0})".format(str(e)))
        return self._type_id


    def get_model_instances(self):
        """
        Return the model instances the plugin has created.
        """
        return self.model.objects.all()



def _import_apps_submodule(submodule):
    """
    Look for a submodule is a series of packages, e.g. a ".node_type_plugins" in all INSTALLED_APPS.
    """
    for app in settings.INSTALLED_APPS:
        try:
            import_module('.' + submodule, app)
        except ImportError, e:
            if submodule not in str(e):
                raise   # import error is a level deeper.
            else:
                pass


# -------- API to access plugins --------

class NodeTypeAlreadyRegistered(Exception):
    """
    Raised when attempting to register a plugin twice.
    """
    pass


class NodeTypeNotFound(Exception):
    """
    Raised when the plugin could not be found in the rendering process.
    """
    pass


class NodeTypePool(object):
    """
    The central administration of plugins.
    """
    _scanLock = Lock()

    #: Define the file to scan for to find plugins
    plugin_module_name = 'node_type_plugins'

    #: Define the base plugin class that is used in this registry.
    base_plugin_class = NodeTypePlugin

    #: Define the base model that is used in this registry.
    base_model = PolymorphicMPTTModel    # TODO: should be first derived non-abstract model instead.


    def __init__(self):
        self.plugins = {}
        self.plugin_for_model = {}
        self._plugin_for_ctype_id = None
        self.detected = False
        self.admin_site = admin.AdminSite()


    def register(self, plugin):
        """
        Make a node type plugin known.

        :param plugin: The plugin class, deriving from :class:`NodeTypePlugin`.

        The plugin will be instantiated, just like Django does this with :class:`~django.contrib.admin.ModelAdmin` classes.
        If a plugin is already registered, this will raise a :class:`PluginAlreadyRegistered` exception.
        """
        # Duct-Typing does not suffice here, avoid hard to debug problems by upfront checks.
        assert issubclass(plugin, self.base_plugin_class), "The plugin must inherit from `{0}`".format(self.base_plugin_class.__name__)
        assert plugin.model, "The plugin has no model defined"
        assert issubclass(plugin.model, self.base_model), "The plugin model must inherit from `{0}`.".format(self.base_model.__name__)

        name = plugin.__name__
        if name in self.plugins:
            raise NodeTypeAlreadyRegistered("{0}: a plugin with this name is already registered".format(name))

        # Reset some caches
        self._folder_types = None
        self._file_types = None
        self._url_types = None

        # Make a single static instance, similar to ModelAdmin.
        plugin_instance = plugin()
        self.plugins[name] = plugin_instance
        self.plugin_for_model[plugin.model] = name       # Track reverse for model.plugin link

        # Only update lazy indexes if already created
        if self._plugin_for_ctype_id is not None:
            self._plugin_for_ctype_id[plugin.type_id] = name

        # Instantiate model admin
        self.admin_site.register(plugin.model, plugin.model_admin)
        return plugin  # Allow class decorator syntax


    def get_plugins(self):
        """
        Return the list of all plugin instances which are loaded.
        """
        self._import_plugins()
        return self.plugins.values()


    def get_model_classes(self):
        """
        Return all :class:`~fluent_contents.models.ContentItem` model classes which are exposed by plugins.
        """
        self._import_plugins()
        return [plugin.model for plugin in self.plugins.values()]


    def get_plugin_by_model(self, model_class):
        """
        Return the corresponding plugin for a given model.
        """
        self._import_plugins()                                # could happen during rendering that no plugin scan happened yet.
        assert issubclass(model_class, PolymorphicMPTTModel)  # avoid confusion between model instance and class here!

        try:
            name = self.plugin_for_model[model_class]
        except KeyError:
            raise NodeTypeNotFound("No plugin found for model '{0}'.".format(model_class.__name__))
        return self.plugins[name]


    def _get_plugin_by_content_type(self, contenttype):
        self._import_plugins()
        self._setup_lazy_indexes()

        ct_id = contenttype.id if isinstance(contenttype, ContentType) else int(contenttype)
        try:
            name = self._plugin_for_ctype_id[ct_id]
        except KeyError:
            raise NodeTypeNotFound("No plugin found for content type '{0}'.".format(contenttype))
        return self.plugins[name]


    def get_model_admin(self, model_class):
        """
        Access the model admin object instantiated for the plugin.
        """
        self._import_plugins()                   # could happen during rendering that no plugin scan happened yet.
        assert issubclass(model_class, PolymorphicMPTTModel)  # avoid confusion between model instance and class here!

        try:
            return self.admin_site._registry[model_class]
        except KeyError:
            raise NodeTypeNotFound("No ModelAdmin found for model '{0}'.".format(model_class.__name__))


    def _import_plugins(self):
        """
        Internal function, ensure all plugin packages are imported.
        """
        if self.detected:
            return

        # In some cases, plugin scanning may start during a request.
        # Make sure there is only one thread scanning for plugins.
        self._scanLock.acquire()
        if self.detected:
            return  # previous threaded released + completed

        try:
            _import_apps_submodule(self.plugin_module_name)
            self.detected = True
        finally:
            self._scanLock.release()


    def _setup_lazy_indexes(self):
        # The ContentType is not read yet at .register() time, since that enforces
        # the database to be created before a plugin scan runs. That might not be the case with a ./manage.py syncdb
        if self._plugin_for_ctype_id is None:
            self._plugin_for_ctype_id = {}
            self._import_plugins()
            for name, plugin in self.plugins.iteritems():
                self._plugin_for_ctype_id[plugin.type_id] = name


#: The global plugin pool, a instance of the :class:`PluginPool` class.
node_type_pool = NodeTypePool()
