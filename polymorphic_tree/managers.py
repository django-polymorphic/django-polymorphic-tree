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


    def __init__(self, *args, **kwargs):
        PolymorphicManager.__init__(self, self.queryset_class, *args, **kwargs)


    def toplevel(self):
        """
        Return all nodes which have no parent.
        """
        return self.get_query_set().toplevel()
