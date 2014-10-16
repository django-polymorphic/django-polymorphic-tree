"""
The manager class for the CMS models
"""
import django
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
        if hasattr(PolymorphicManager, 'get_queryset') and django.VERSION >= (1,6):
            # Latest django-polymorphic for Django 1.7
            # Should not be used for Django 1.4/1.5 all all, as that breaks the RelatedManager
            qs = self.get_queryset()
        else:
            qs = self.get_query_set()

        return qs.toplevel()
