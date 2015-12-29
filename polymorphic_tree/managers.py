"""
The manager class for the CMS models
"""
import django
from django.db.models.query import QuerySet
from mptt.managers import TreeManager
from polymorphic.manager import PolymorphicManager
from polymorphic.query import PolymorphicQuerySet

try:
    # mptt 0.7 has queryset methods too
    from mptt.querysets import TreeQuerySet
except ImportError:
    # provide compatibility with older mptt versions by adding a stub.
    class TreeQuerySet(QuerySet):
        pass


class PolymorphicMPTTQuerySet(TreeQuerySet, PolymorphicQuerySet):
    """
    Base class for querysets
    """
    def toplevel(self):
        """
        Return all nodes which have no parent.
        """
        return self.filter(parent__isnull=True)


class PolymorphicMPTTModelManager(TreeManager, PolymorphicManager):
    """
    Base class for a model manager.
    """
    #: The queryset class to use.
    queryset_class = PolymorphicMPTTQuerySet

    # Re-apply the logic from django-polymorphic and django-mptt.
    # As of django-mptt 0.7, TreeManager.get_querset() no longer calls super()
    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db).order_by(self.tree_id_attr, self.left_attr)

    # For Django 1.5
    if django.VERSION < (1, 7):
        get_query_set = get_queryset

    def toplevel(self):
        """
        Return all nodes which have no parent.
        """
        # By using .all(), the proper get_query_set()/get_queryset() will be used for each Django version.
        # Django 1.4/1.5 need to use get_query_set(), because the RelatedManager overrides that.
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

        return super(PolymorphicMPTTModelManager, self)._mptt_filter(qs, **filters)
