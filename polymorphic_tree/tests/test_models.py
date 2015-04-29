# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.db.models import Q
from django.test import TestCase

from polymorphic import ShowFieldContent, ShowFieldType, ShowFieldTypeAndContent

from polymorphic_tree.models import PolymorphicMPTTModel, PolymorphicTreeForeignKey


class PlainA(models.Model):
    field1 = models.CharField(max_length=10)

class PlainB(PlainA):
    field2 = models.CharField(max_length=10)

class PlainC(PlainB):
    field3 = models.CharField(max_length=10)


class Model2A(ShowFieldType, PolymorphicMPTTModel):
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


class PolymorphicTreeTests(TestCase):
    """
    Test Suite, largely derived from django-polymorphic tests
    """

    def create_model2abcd(self):
        """
        Create the chain of objects of Model2,
        this is reused in various tests.
        """
        Model2A.objects.create(field1='A1')
        Model2B.objects.create(field1='B1', field2='B2')
        Model2C.objects.create(field1='C1', field2='C2', field3='C3')
        Model2D.objects.create(field1='D1', field2='D2', field3='D3', field4='D4')

    def test_simple_inheritance(self):
        self.create_model2abcd()

        objects = list(Model2A.objects.all())
        self.assertEqual(repr(objects[0]), '<Model2A: id 1, parent (PolymorphicTreeForeignKey), field1 (CharField), lft (PositiveIntegerField), rght (PositiveIntegerField), tree_id (PositiveIntegerField), level (PositiveIntegerField)>')
        self.assertEqual(repr(objects[1]), '<Model2B: id 2, parent (PolymorphicTreeForeignKey), field1 (CharField), lft (PositiveIntegerField), rght (PositiveIntegerField), tree_id (PositiveIntegerField), level (PositiveIntegerField), field2 (CharField)>')
        self.assertEqual(repr(objects[2]), '<Model2C: id 3, parent (PolymorphicTreeForeignKey), field1 (CharField), lft (PositiveIntegerField), rght (PositiveIntegerField), tree_id (PositiveIntegerField), level (PositiveIntegerField), field2 (CharField), field3 (CharField)>')
        self.assertEqual(repr(objects[3]), '<Model2D: id 4, parent (PolymorphicTreeForeignKey), field1 (CharField), lft (PositiveIntegerField), rght (PositiveIntegerField), tree_id (PositiveIntegerField), level (PositiveIntegerField), field2 (CharField), field3 (CharField), field4 (CharField)>')

    def test_manual_get_real_instance(self):
        self.create_model2abcd()

        o = Model2A.objects.non_polymorphic().get(field1='C1')
        self.assertEqual(repr(o.get_real_instance()), '<Model2C: id 3, parent (PolymorphicTreeForeignKey), field1 (CharField), lft (PositiveIntegerField), rght (PositiveIntegerField), tree_id (PositiveIntegerField), level (PositiveIntegerField), field2 (CharField), field3 (CharField)>')

    def test_non_polymorphic(self):
        self.create_model2abcd()

        objects = list(Model2A.objects.all().non_polymorphic())
        self.assertEqual(repr(objects[0]), '<Model2A: id 1, parent (PolymorphicTreeForeignKey), field1 (CharField), lft (PositiveIntegerField), rght (PositiveIntegerField), tree_id (PositiveIntegerField), level (PositiveIntegerField)>')
        self.assertEqual(repr(objects[1]), '<Model2A: id 2, parent (PolymorphicTreeForeignKey), field1 (CharField), lft (PositiveIntegerField), rght (PositiveIntegerField), tree_id (PositiveIntegerField), level (PositiveIntegerField)>')
        self.assertEqual(repr(objects[2]), '<Model2A: id 3, parent (PolymorphicTreeForeignKey), field1 (CharField), lft (PositiveIntegerField), rght (PositiveIntegerField), tree_id (PositiveIntegerField), level (PositiveIntegerField)>')
        self.assertEqual(repr(objects[3]), '<Model2A: id 4, parent (PolymorphicTreeForeignKey), field1 (CharField), lft (PositiveIntegerField), rght (PositiveIntegerField), tree_id (PositiveIntegerField), level (PositiveIntegerField)>')

    def test_get_real_instances(self):
        self.create_model2abcd()
        qs = Model2A.objects.all().non_polymorphic()

        # from queryset
        objects = qs.get_real_instances()
        self.assertEqual(repr(objects[0]), '<Model2A: id 1, parent (PolymorphicTreeForeignKey), field1 (CharField), lft (PositiveIntegerField), rght (PositiveIntegerField), tree_id (PositiveIntegerField), level (PositiveIntegerField)>')
        self.assertEqual(repr(objects[1]), '<Model2B: id 2, parent (PolymorphicTreeForeignKey), field1 (CharField), lft (PositiveIntegerField), rght (PositiveIntegerField), tree_id (PositiveIntegerField), level (PositiveIntegerField), field2 (CharField)>')
        self.assertEqual(repr(objects[2]), '<Model2C: id 3, parent (PolymorphicTreeForeignKey), field1 (CharField), lft (PositiveIntegerField), rght (PositiveIntegerField), tree_id (PositiveIntegerField), level (PositiveIntegerField), field2 (CharField), field3 (CharField)>')
        self.assertEqual(repr(objects[3]), '<Model2D: id 4, parent (PolymorphicTreeForeignKey), field1 (CharField), lft (PositiveIntegerField), rght (PositiveIntegerField), tree_id (PositiveIntegerField), level (PositiveIntegerField), field2 (CharField), field3 (CharField), field4 (CharField)>')

        # from a manual list
        objects = Model2A.objects.get_real_instances(list(qs))
        self.assertEqual(repr(objects[0]), '<Model2A: id 1, parent (PolymorphicTreeForeignKey), field1 (CharField), lft (PositiveIntegerField), rght (PositiveIntegerField), tree_id (PositiveIntegerField), level (PositiveIntegerField)>')
        self.assertEqual(repr(objects[1]), '<Model2B: id 2, parent (PolymorphicTreeForeignKey), field1 (CharField), lft (PositiveIntegerField), rght (PositiveIntegerField), tree_id (PositiveIntegerField), level (PositiveIntegerField), field2 (CharField)>')
        self.assertEqual(repr(objects[2]), '<Model2C: id 3, parent (PolymorphicTreeForeignKey), field1 (CharField), lft (PositiveIntegerField), rght (PositiveIntegerField), tree_id (PositiveIntegerField), level (PositiveIntegerField), field2 (CharField), field3 (CharField)>')
        self.assertEqual(repr(objects[3]), '<Model2D: id 4, parent (PolymorphicTreeForeignKey), field1 (CharField), lft (PositiveIntegerField), rght (PositiveIntegerField), tree_id (PositiveIntegerField), level (PositiveIntegerField), field2 (CharField), field3 (CharField), field4 (CharField)>')

    def test_translate_polymorphic_q_object(self):
        self.create_model2abcd()

        q = Model2A.translate_polymorphic_Q_object(Q(instance_of=Model2C))
        objects = Model2A.objects.filter(q)
        self.assertEqual(repr(objects[0]), '<Model2C: id 3, parent (PolymorphicTreeForeignKey), field1 (CharField), lft (PositiveIntegerField), rght (PositiveIntegerField), tree_id (PositiveIntegerField), level (PositiveIntegerField), field2 (CharField), field3 (CharField)>')
        self.assertEqual(repr(objects[1]), '<Model2D: id 4, parent (PolymorphicTreeForeignKey), field1 (CharField), lft (PositiveIntegerField), rght (PositiveIntegerField), tree_id (PositiveIntegerField), level (PositiveIntegerField), field2 (CharField), field3 (CharField), field4 (CharField)>')

    def test_base_manager(self):
        def show_base_manager(model):
            return "{0} {1}".format(
                repr(type(model._base_manager)),
                repr(model._base_manager.model)
            )

        self.assertEqual(show_base_manager(PlainA), "<class 'django.db.models.manager.Manager'> <class 'polymorphic_tree.tests.test_models.PlainA'>")
        self.assertEqual(show_base_manager(PlainB), "<class 'django.db.models.manager.Manager'> <class 'polymorphic_tree.tests.test_models.PlainB'>")
        self.assertEqual(show_base_manager(PlainC), "<class 'django.db.models.manager.Manager'> <class 'polymorphic_tree.tests.test_models.PlainC'>")

        self.assertEqual(show_base_manager(Model2A), "<class 'polymorphic_tree.managers.PolymorphicMPTTModelManager'> <class 'polymorphic_tree.tests.test_models.Model2A'>")
        self.assertEqual(show_base_manager(Model2B), "<class 'django.db.models.manager.Manager'> <class 'polymorphic_tree.tests.test_models.Model2B'>")
        self.assertEqual(show_base_manager(Model2C), "<class 'django.db.models.manager.Manager'> <class 'polymorphic_tree.tests.test_models.Model2C'>")

        self.assertEqual(show_base_manager(One2OneRelatingModel), "<class 'polymorphic_tree.managers.PolymorphicMPTTModelManager'> <class 'polymorphic_tree.tests.test_models.One2OneRelatingModel'>")
        self.assertEqual(show_base_manager(One2OneRelatingModelDerived), "<class 'django.db.models.manager.Manager'> <class 'polymorphic_tree.tests.test_models.One2OneRelatingModelDerived'>")
