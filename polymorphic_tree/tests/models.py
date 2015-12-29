from django.db import models

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
