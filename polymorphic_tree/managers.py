"""
The manager class for the CMS models
"""
from mptt.managers import TreeManager
from polymorphic import PolymorphicManager
from polymorphic.query import PolymorphicQuerySet


class PolymorphicMPTTQuerySet(PolymorphicQuerySet):
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


    def toplevel(self):
        """
        Return all nodes which have no parent.
        """
        # By using .all(), the proper get_query_set()/get_queryset() will be used for each Django version.
        # Django 1.4/1.5 need to use get_query_set(), because the RelatedManager overrides that.
        return self.all().toplevel()
