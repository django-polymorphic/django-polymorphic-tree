from django.core.exceptions import ValidationError
from django.db import models
from mptt.exceptions import InvalidMove

from polymorphic.showfields import ShowFieldContent
from polymorphic_tree.models import PolymorphicMPTTModel, PolymorphicTreeForeignKey


class PlainA(models.Model):
    field1 = models.CharField(max_length=10)

class PlainB(PlainA):
    field2 = models.CharField(max_length=10)

class PlainC(PlainB):
    field3 = models.CharField(max_length=10)


class Model2A(ShowFieldContent, PolymorphicMPTTModel):
    parent = PolymorphicTreeForeignKey('self', blank=True, null=True, related_name='children', verbose_name='parent')
    field1 = models.CharField(max_length=10)

class Model2B(Model2A):
    field2 = models.CharField(max_length=10)

class Model2C(Model2B):
    field3 = models.CharField(max_length=10)

class Model2D(Model2C):
    field4 = models.CharField(max_length=10)


class One2OneRelatingModel(PolymorphicMPTTModel):
    parent = PolymorphicTreeForeignKey('self', blank=True, null=True, related_name='children', verbose_name='parent')
    one2one = models.OneToOneField(Model2A)
    field1 = models.CharField(max_length=10)

class One2OneRelatingModelDerived(One2OneRelatingModel):
    field2 = models.CharField(max_length=10)


class Base(ShowFieldContent, PolymorphicMPTTModel):
    parent = PolymorphicTreeForeignKey('self', blank=True, null=True, related_name='children', verbose_name='parent')
    field_b = models.CharField(max_length=10)

class ModelX(Base):
    field_x = models.CharField(max_length=10)

class ModelY(Base):
    field_y = models.CharField(max_length=10)


class ModelWithCustomParentName(PolymorphicMPTTModel):
    """Model with custom parent name

    A model where ``PolymorphicTreeForeignKey`` attribute has not ``parent``
    name, but ``chief``

    Attributes:
        chief (ModelWithCustomParentName): parent
        field5 (str): test field
    """
    chief = PolymorphicTreeForeignKey('self',
                                      blank=True,
                                      null=True,
                                      related_name='subordinate',
                                      verbose_name='Chief')
    field5 = models.CharField(max_length=10)

    class MPTTMeta:
        parent_attr = 'chief'

    def __str__(self):
        return self.field5


class ModelWithValidation(PolymorphicMPTTModel):
    """Model with custom validation

    A model with redefined ``clean`` and ``can_be_moved`` methods

    ``clean`` method always raises ``ValidationError``

    Attributes:
        parent (ModelWithValidation): parent
        field6 (str): test field
    """

    parent = PolymorphicTreeForeignKey('self',
                                       blank=True,
                                       null=True,
                                       related_name='children')

    field6 = models.CharField(max_length=10)

    def clean(self):
        """Raise validation error"""
        raise ValidationError({
            'parent': 'There is something with parent field'
        })


class ModelWithInvalidMove(PolymorphicMPTTModel):
    """Model with custom validation

    A model with redefined only ``can_be_moved`` method which always raises
    ``InvalidMove``

    Attributes:
        parent (ModelWithValidation): parent
        field7 (str): test field
    """

    parent = PolymorphicTreeForeignKey('self',
                                       blank=True,
                                       null=True,
                                       related_name='children')

    field7 = models.CharField(max_length=10)

    def move_to(self, target, position='first-child'):
        raise InvalidMove('Invalid move')
