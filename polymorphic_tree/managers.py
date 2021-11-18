"""
The manager class for the CMS models
"""
from mptt.managers import TreeManager
from mptt.querysets import TreeQuerySet
from polymorphic.managers import PolymorphicManager
from polymorphic.query import PolymorphicQuerySet


class PolymorphicMPTTQuerySet(TreeQuerySet, PolymorphicQuerySet):
    """
    Base class for querysets
    """

    def toplevel(self):
        """
        Return all nodes which have no parent.
        """
        return self.filter(parent__isnull=True)

    def as_manager(cls):
        # Make sure this way of creating managers works.
        manager = PolymorphicMPTTModelManager.from_queryset(cls)()
        manager._built_with_as_manager = True
        return manager

    as_manager.queryset_only = True
    as_manager = classmethod(as_manager)


class PolymorphicMPTTModelManager(TreeManager, PolymorphicManager):
    """
    Base class for a model manager.
    """

    #: The queryset class to use.
    queryset_class = PolymorphicMPTTQuerySet

    def toplevel(self):
        """
        Return all nodes which have no parent.
        """
        # Calling .all() is equivalent to .get_queryset()
        return self.all().toplevel()

    def _mptt_filter(self, qs=None, **filters):
        if self._base_manager and qs is not None:
            # This is a little hack to fix get_previous_sibling() / get_next_sibling().
            # When the queryset is defined (meaning: a call was made from model._tree_manager._mptt_filter(qs)),
            # there is a call to find related objects.# The current model might be a derived model however,
            # due to out polymorphic layout. Enforce seeking from the base model that holds the entire MPTT structure,
            # and the polymorphic queryset will upgrade the models again.
            if issubclass(qs.model, self.model):
                qs.model = self._base_manager.model
                qs.query.model = self._base_manager.model

        return super()._mptt_filter(qs, **filters)

    def move_node(self, node, target, position="last-child"):
        """
        Move a node to a new location.
        This also performs checks whether the target allows this node to reside there.
        """
        node.validate_move(target, position=position)
        return super().move_node(node, target, position=position)
