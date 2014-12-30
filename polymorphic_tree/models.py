"""
Model that inherits from both Polymorphic and MPTT.
"""
from future.utils import with_metaclass
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel, MPTTModelBase, TreeForeignKey
from polymorphic import PolymorphicModel
from polymorphic.base import PolymorphicModelBase
from polymorphic_tree.managers import PolymorphicMPTTModelManager

from six import integer_types, string_types

def _get_base_polymorphic_model(ChildModel):
    """
    First model in the inheritance chain that inherited from the PolymorphicMPTTModel
    """
    for Model in reversed(ChildModel.mro()):
        if isinstance(Model, PolymorphicMPTTModelBase) and Model is not PolymorphicMPTTModel:
            return Model
    return None



class PolymorphicMPTTModelBase(MPTTModelBase, PolymorphicModelBase):
    """
    Metaclass for all polymorphic models.
    Needed to support both MPTT and Polymorphic metaclasses.
    """
    pass


class PolymorphicTreeForeignKey(TreeForeignKey):
    """
    A foreignkey that limits the node types the parent can be.
    """
    default_error_messages = {
        'no_children_allowed': _("The selected node cannot have child nodes."),
    }

    def clean(self, value, model_instance):
        value = super(PolymorphicTreeForeignKey, self).clean(value, model_instance)
        self._validate_parent(value, model_instance)
        return value


    def _validate_parent(self, parent, model_instance):
        if not parent:
            return
        elif isinstance(parent, integer_types):
            # TODO: Improve this code, it's a bit of a hack now because the base model is not known in the NodeTypePool.
            base_model = _get_base_polymorphic_model(model_instance.__class__)
            parent = base_model.objects.get(pk=parent)
        elif not isinstance(parent, PolymorphicMPTTModel):
            raise ValueError("Unknown parent value")

        if parent.can_have_children:
            return

        can_have_children = parent.can_have_children
        if can_have_children:
            child_types = parent.get_child_types()
            if (len(child_types) == 0 or
                    model_instance.polymorphic_ctype_id in child_types):
                return # child is allowed
            raise ValidationError(
                self.error_messages['child_not_allowed'].format(parent,
                    parent._meta.verbose_name,
                    model_instance._meta.verbose_name))

        raise ValidationError(self.error_messages['no_children_allowed'])



class PolymorphicMPTTModel(with_metaclass(PolymorphicMPTTModelBase, MPTTModel, PolymorphicModel)):
    """
    The base class for all nodes; a mapping of an URL to content (e.g. a HTML page, text file, blog, etc..)
    """

    #: Whether the node type allows to have children.
    can_have_children = True
    #: Allowed child types for this page.
    child_types = []
    # Cache child types using a class variable to ensure that get_child_types
    # is run once per page class, per django initiation.
    __child_types = {}

    # Django fields
    _default_manager = PolymorphicMPTTModelManager()

    @property
    def page_key(self):
        """
        A unique key for this page to ensure get_child_types is run once per
        page.
        """
        return repr(self)

    def get_child_types(self):
        """
        Get the allowed child types and convert them into content type ids.
        This allows for the lookup of allowed children in the admin tree.
        """
        key = self.page_key
        child_types = self._PolymorphicMPTTModel__child_types
        if self.can_have_children and child_types.setdefault(key, None) is None:
            new_children = []
            iterator = iter(self.child_types)
            for child in iterator:
                if isinstance(child, string_types):
                    child = str(child).lower()
                    # write self to refer to self
                    if child == 'self':
                        ct_id = self.polymorphic_ctype_id
                    else:
                        # either the name of a model in this app
                        # or the full app.model dot string
                        # just like a foreign key
                        try:
                            app_label, model = child.rsplit('.', 1)
                        except ValueError:
                            app_label = self._meta.app_label
                            model = child
                        ct_id = ContentType.objects.get(app_label=app_label,
                            model=model).id
                else:
                    # pass in a model class
                    ct_id = ContentType.objects.get_for_model(child).id
                new_children.append(ct_id)
            child_types[key] = new_children
        return child_types[key]


    class Meta:
        abstract = True
        ordering = ('lft',)

    # Define:
    # parent = PolymorphicTreeForeignKey('self', blank=True, null=True, related_name='children', verbose_name=_('parent'), help_text=_('You can also change the parent by dragging the item in the list.'))
    # class MPTTMeta:
    #     order_insertion_by = 'title'


# South integration
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^polymorphic_tree\.models\.PolymorphicTreeForeignKey"])
except ImportError:
    pass
