"""
Model that inherits from both Polymorphic and MPTT.
"""
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel, MPTTModelBase, TreeForeignKey
from polymorphic import PolymorphicModel
from polymorphic.base import PolymorphicModelBase
from polymorphic_tree.managers import PolymorphicMPTTModelManager


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
        elif isinstance(parent, (int, long)):
            # TODO: Improve this code, it's a bit of a hack now because the base model is not known in the NodeTypePool.
            base_model = _get_base_polymorphic_model(model_instance.__class__)

            # Get parent, TODO: needs to downcast here to read can_have_children.
            parent = base_model.objects.get(pk=parent)
        elif not isinstance(parent, PolymorphicMPTTModel):
            raise ValueError("Unknown parent value")

        if parent.can_have_children:
            return

        raise ValidationError(self.error_messages['no_children_allowed'])



class PolymorphicMPTTModel(MPTTModel, PolymorphicModel):
    """
    The base class for all nodes; a mapping of an URL to content (e.g. a HTML page, text file, blog, etc..)
    """
    __metaclass__ = PolymorphicMPTTModelBase

    #: Whether the node type allows to have children.
    can_have_children = True

    # Django fields
    _default_manager = PolymorphicMPTTModelManager()

    class Meta:
        abstract = True
        ordering = ('lft',)

    # Define:
    # parent = PolymorphicTreeForeignKey('self', blank=True, null=True, related_name='children', verbose_name=_('parent'), help_text=_('You can also change the parent by dragging the item in the list.'))
    # class MPTTMeta:
    #     order_insertion_by = 'title'

    def save(self, *args, **kwargs):
        # from parentadmin.PolymorphicMPTTParentModelAdmin.api_node_moved_view()
        kwargs.pop('previous_parent_id', None)
        return super(PolymorphicMPTTModel, self).save(*args, **kwargs)

# South integration
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^polymorphic_tree\.models\.PolymorphicTreeForeignKey"])
except ImportError:
    pass
