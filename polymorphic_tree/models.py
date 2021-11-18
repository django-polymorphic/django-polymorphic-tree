"""
Model that inherits from both Polymorphic and MPTT.
"""
import uuid

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.encoding import force_str
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from mptt.exceptions import InvalidMove
from mptt.models import MPTTModel, MPTTModelBase, TreeForeignKey, raise_if_unsaved
from polymorphic.base import PolymorphicModelBase
from polymorphic.models import PolymorphicModel

from polymorphic_tree.managers import PolymorphicMPTTModelManager


def _get_base_polymorphic_model(ChildModel):
    """
    First model in the inheritance chain that inherited from the PolymorphicMPTTModel
    """
    for Model in reversed(ChildModel.mro()):
        if (
            isinstance(Model, PolymorphicMPTTModelBase)
            and Model is not PolymorphicMPTTModel
            and not Model._meta.abstract
        ):
            return Model
    return None


class PolymorphicMPTTModelBase(MPTTModelBase, PolymorphicModelBase):
    """
    Metaclass for all polymorphic models.
    Needed to support both MPTT and Polymorphic metaclasses.
    """


class PolymorphicTreeForeignKey(TreeForeignKey):
    """
    A foreignkey that limits the node types the parent can be.
    """

    default_error_messages = {
        "required": _("This node type should have a parent."),
        "no_children_allowed": _("The selected parent cannot have child nodes."),
        "child_not_allowed": _("The selected parent cannot have this node type as a child!"),
    }

    def clean(self, value, model_instance):
        value = super().clean(value, model_instance)
        self._validate_parent(value, model_instance)
        return value

    def _validate_parent(self, parent, model_instance):
        if not parent:
            # This can't test for model_instance.can_be_root,
            # because clean() is not called for empty values.
            return
        elif isinstance(parent, int) or isinstance(parent, uuid.UUID):
            # TODO: Improve this code, it's a bit of a hack now because the base model is not known in the NodeTypePool.
            base_model = _get_base_polymorphic_model(model_instance.__class__)
            parent = base_model.objects.get(pk=parent)
        elif not isinstance(parent, PolymorphicMPTTModel):
            raise ValueError("Unknown parent value")

        if not parent.can_have_children:
            raise ValidationError(self.error_messages["no_children_allowed"])

        if not parent.is_child_allowed(model_instance):
            raise ValidationError(self.error_messages["child_not_allowed"])


class PolymorphicMPTTModel(MPTTModel, PolymorphicModel, metaclass=PolymorphicMPTTModelBase):
    """
    The base class for all nodes; a mapping of an URL to content (e.g. a HTML page, text file, blog, etc..)
    """

    #: Whether the node type allows to have children.
    can_have_children = True

    #: Whether the node type can be a root node.
    can_be_root = True

    #: Allowed child types for this page.
    child_types = []

    # Cache child types using a class variable to ensure that get_child_types
    # is run once per page class, per django initiation.
    __child_types = {}

    # Django fields
    objects = PolymorphicMPTTModelManager()

    class Meta:
        abstract = True
        ordering = (
            "tree_id",
            "lft",
        )
        base_manager_name = "objects"

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
        if not self.can_have_children:
            return []

        if child_types.get(key, None) is None:
            new_children = []
            iterator = iter(self.child_types)
            for child in iterator:
                if isinstance(child, str):
                    child = str(child).lower()
                    # write self to refer to self
                    if child == "self":
                        ct_id = self.polymorphic_ctype_id
                    else:
                        # either the name of a model in this app
                        # or the full app.model dot string
                        # just like a foreign key
                        try:
                            app_label, model = child.rsplit(".", 1)
                        except ValueError:
                            app_label = self._meta.app_label
                            model = child
                        ct_id = ContentType.objects.get_by_natural_key(app_label, model).id
                else:
                    # pass in a model class
                    ct_id = ContentType.objects.get_for_model(child).id
                new_children.append(ct_id)
            child_types[key] = new_children

        return child_types[key]

    # Define:
    # parent = PolymorphicTreeForeignKey('self', blank=True, null=True, related_name='children', verbose_name=_('parent'),
    #                                    help_text=_('You can also change the parent by dragging the item in the list.'))
    # class MPTTMeta:
    #     order_insertion_by = 'title'

    @raise_if_unsaved
    def get_closest_ancestor_of_type(self, model, include_self=False):
        """
        Find the first parent of a specific model type.
        """
        if include_self and isinstance(self, model):
            return self
        else:
            try:
                return self.get_ancestors_of_type(model, ascending=False)[0]
            except IndexError:
                return None

    @raise_if_unsaved
    def get_ancestors_of_type(self, model, ascending=False, include_self=False):
        """
        Find a parent of a specific type.
        """
        return self.get_ancestors(ascending=ascending, include_self=include_self).instance_of(model)

    def is_child_allowed(self, child):
        """
        Tell whether this node allows the given node as child.
        """
        if not self.can_have_children:
            return False

        child_types = self.get_child_types()

        # this allows tree validation to occur in the event the child model is not
        # yet created in db (ie. when django admin tries to validate)
        child.pre_save_polymorphic()

        return not child_types or child.polymorphic_ctype_id in child_types

    def validate_move(self, target, position="first-child"):
        """
        Validate whether the move to a new location is permitted.

        :param target: The node to move to
        :type target: PolymorphicMPTTModel
        :param position: The relative position to the target. This can be ``'first-child'``,
                         ``'last-child'``, ``'left'`` or ``'right'``.
        """
        new_parent = _get_new_parent(self, target, position)

        if new_parent is None:
            if not self.can_be_root:
                raise InvalidMove(gettext("This node type should have a parent."))
        else:
            if not new_parent.can_have_children:
                raise InvalidMove(
                    gettext(
                        "Cannot place \u2018{0}\u2019 below \u2018{1}\u2019; a {2} does not allow children!"
                    ).format(self, new_parent, new_parent._meta.verbose_name)
                )

            if not new_parent.is_child_allowed(self):
                raise InvalidMove(
                    gettext(
                        "Cannot place \u2018{0}\u2019 below \u2018{1}\u2019; a {2} does not allow {3} as a child!"
                    ).format(self, target, target._meta.verbose_name, self._meta.verbose_name)
                )

        # Allow custom validation
        self.validate_move_to(new_parent)

    def validate_move_to(self, new_parent):
        """
        Can move be finished

        Method have to be redefined in inherited model to define cases when
        node can be moved. If method is not redefined moving is always allowed.
        The ``new_parent`` can be ``None`` when the node is moved to the root.

        To deny move, this method have to be raised ``ValidationError`` or
        ``InvalidMove`` from ``mptt.exceptions``
        """

    def clean(self):
        super().clean()

        try:
            # Make sure form validation also reports choosing a wrong parent.
            # This also updates what PolymorphicTreeForeignKey already does.
            parent_id = getattr(self, self._mptt_meta.parent_attr + "_id")
            parent = getattr(self, self._mptt_meta.parent_attr) if parent_id else None
            self.validate_move(parent)
        except InvalidMove as e:
            raise ValidationError({self._mptt_meta.parent_attr: force_str(e)})


def _get_new_parent(moved, target, position="first-child"):
    """
    Find out which parent the node will reside under.
    """
    if position in ("first-child", "last-child"):
        return target
    elif position in ("left", "right"):
        # left/right of an other node
        parent_attr_id = f"{moved._mptt_meta.parent_attr}_id"
        if getattr(target, parent_attr_id) == getattr(moved, parent_attr_id):
            # kept inside the same parent, hopefully use the cache we already have.
            return getattr(moved, moved._mptt_meta.parent_attr)

        return getattr(target, target._mptt_meta.parent_attr)
    else:
        raise ValueError("invalid mptt position argument")
