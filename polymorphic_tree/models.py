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
        print Model
        if isinstance(Model, PolymorphicMPTTModelBase) and Model is not PolymorphicMPTTModel:
            return Model
    return None


def _validate_parent(parent):
    from polymorphic_tree.extensions import node_type_pool
    if not parent:
        return
    elif isinstance(parent, (int, long)):
        # TODO: Improve this code, it's a bit of a hack now because the base model is not known in the NodeTypePool.
        base_model = _get_base_polymorphic_model(node_type_pool.get_model_classes()[0])
        parent = base_model.objects.non_polymorphic().values('polymorphic_ctype').get(pk=parent)
        plugin = node_type_pool._get_plugin_by_content_type(parent['polymorphic_ctype'])
        if plugin.can_have_children:
            return
    elif isinstance(parent, PolymorphicMPTTModel):
        if parent.can_have_children:
            return
    else:
        raise ValueError("Unknown parent value")

    raise ValidationError(_("The selected node cannot have child nodes."))


class PolymorphicMPTTModelBase(MPTTModelBase, PolymorphicModelBase):
    """
    Metaclass for all plugin models.

    Set db_table if it has not been customized.
    """
    #: The table format to use, allow reuse with a different table style.
    table_name_template = "nodetype_{app_label}_{model_name}"

    def __new__(mcs, name, bases, attrs):
        new_class = super(PolymorphicMPTTModelBase, mcs).__new__(mcs, name, bases, attrs)

        if not any(isinstance(base, mcs) for base in bases):
            # Don't apply to the PolymorphicMPTTModel
            return new_class
        else:
            # Update the table name.
            # Inspired by from Django-CMS, (c) , BSD licensed.
            meta = new_class._meta
            if meta.db_table.startswith(meta.app_label + '_') and not getattr(meta, 'abstract', False):
                model_name = meta.db_table[len(meta.app_label)+1:]
                meta.db_table = mcs.table_name_template.format(app_label=meta.app_label, model_name=model_name)

        return new_class


class PolymorphicMPTTModel(MPTTModel, PolymorphicModel):
    """
    The base class for all nodes; a mapping of an URL to content (e.g. a HTML page, text file, blog, etc..)
    """
    __metaclass__ = PolymorphicMPTTModelBase

    parent = TreeForeignKey('self', blank=True, null=True, related_name='children', verbose_name=_('parent'), validators=[_validate_parent], help_text=_('You can also change the parent by dragging the item in the list.'))

    objects = PolymorphicMPTTModelManager()

    class Meta:
        abstract = True
        ordering = ('lft',)

    #class MPTTMeta:
    #    order_insertion_by = 'title'


    @property
    def is_first_child(self):
        return self.is_root_node() or (self.parent and (self.lft == self.parent.lft + 1))


    @property
    def is_last_child(self):
        return self.is_root_node() or (self.parent and (self.rght + 1 == self.parent.rght))


    @property
    def can_have_children(self):
        return self.plugin.can_have_children


    @property
    def plugin(self):
        """
        Access the parent plugin which provides all metadata.
        """
        from polymorphic_tree.extensions import node_type_pool
        # Also allow a non_polymorphic() queryset to resolve the plugin.
        # Corresponding page_type_pool method is still private on purpose.
        # Not sure the utility method should be public, or how it should be named.
        return node_type_pool._get_plugin_by_content_type(self.polymorphic_ctype_id)
