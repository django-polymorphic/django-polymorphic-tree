"""
Model that inherits from both Polymorphic and MPTT.
"""
from __future__ import unicode_literals
from future.utils import with_metaclass
from future.utils.six import integer_types
from future.builtins import str
from django.contrib.contenttypes.models import ContentType
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
        'no_children_allowed': _('The selected node cannot have child nodes.'),
        'child_not_allowed': _('Cannot place this page below '
            '\u2018{0}\u2019; a {1} does not allow {2} as a child!')
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

            parent = base_model.objects.get(pk=parent).get_real_instance()
        elif not isinstance(parent, PolymorphicMPTTModel):
            raise ValueError("Unknown parent value")

        if parent.can_have_children:
            try:
                iter(parent.can_have_children)
            except TypeError:
                return # boolean True
            if model_instance.polymorphic_ctype_id in parent.can_have_children:
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

    # Django fields
    _default_manager = PolymorphicMPTTModelManager()

    def __init__(self, *args, **kwargs):
        super(PolymorphicMPTTModel, self).__init__(*args, **kwargs)
        try:
            iterator = iter(self.can_have_children)
        except TypeError:
            pass # can_have_children is not an iterable
        else:
            new_children = []
            for child in iterator:
                if isinstance(unicode(child), str):
                    child = unicode(child).lower()
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
            self.can_have_children = new_children

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
