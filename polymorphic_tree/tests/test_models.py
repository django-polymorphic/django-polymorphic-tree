# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import Q
from django.test import TestCase

from .models import *


class PolymorphicTests(TestCase):
    """
    Test Suite, largely derived from django-polymorphic tests

    TODO: potentially port these tests from django_polymorphic.tests

        test_foreignkey_field()
        test_onetoone_field()
        test_manytomany_field()
        test_extra_method()
        test_instance_of_filter()
        test_polymorphic___filter()
        test_delete()
        test_combine_querysets()
        test_multiple_inheritance()
        test_relation_base()
        test_user_defined_manager()
        test_manager_inheritance()
        test_queryset_assignment()
        test_proxy_models()
        test_proxy_get_real_instance_class()
        test_content_types_for_proxy_models()
        test_proxy_model_inheritance()
        test_custom_pk()
        test_fix_getattribute()
        test_parent_link_and_related_name()

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
        self.assertEqual(repr(objects[0]), '<Model2A: id 1, parent None, field1 "A1", lft 1, rght 2, tree_id 1, level 0>')
        self.assertEqual(repr(objects[1]), '<Model2B: id 2, parent None, field1 "B1", lft 1, rght 2, tree_id 2, level 0, field2 "B2">')
        self.assertEqual(repr(objects[2]), '<Model2C: id 3, parent None, field1 "C1", lft 1, rght 2, tree_id 3, level 0, field2 "C2", field3 "C3">')
        self.assertEqual(repr(objects[3]), '<Model2D: id 4, parent None, field1 "D1", lft 1, rght 2, tree_id 4, level 0, field2 "D2", field3 "D3", field4 "D4">')

    def test_manual_get_real_instance(self):
        self.create_model2abcd()

        o = Model2A.objects.non_polymorphic().get(field1='C1')
        self.assertEqual(repr(o.get_real_instance()), '<Model2C: id 3, parent None, field1 "C1", lft 1, rght 2, tree_id 3, level 0, field2 "C2", field3 "C3">')

    def test_non_polymorphic(self):
        self.create_model2abcd()

        objects = list(Model2A.objects.all().non_polymorphic())
        self.assertEqual(repr(objects[0]), '<Model2A: id 1, parent None, field1 "A1", lft 1, rght 2, tree_id 1, level 0>')
        self.assertEqual(repr(objects[1]), '<Model2A: id 2, parent None, field1 "B1", lft 1, rght 2, tree_id 2, level 0>')
        self.assertEqual(repr(objects[2]), '<Model2A: id 3, parent None, field1 "C1", lft 1, rght 2, tree_id 3, level 0>')
        self.assertEqual(repr(objects[3]), '<Model2A: id 4, parent None, field1 "D1", lft 1, rght 2, tree_id 4, level 0>')

    def test_get_real_instances(self):
        self.create_model2abcd()
        qs = Model2A.objects.all().non_polymorphic()

        # from queryset
        objects = qs.get_real_instances()
        self.assertEqual(repr(objects[0]), '<Model2A: id 1, parent None, field1 "A1", lft 1, rght 2, tree_id 1, level 0>')
        self.assertEqual(repr(objects[1]), '<Model2B: id 2, parent None, field1 "B1", lft 1, rght 2, tree_id 2, level 0, field2 "B2">')
        self.assertEqual(repr(objects[2]), '<Model2C: id 3, parent None, field1 "C1", lft 1, rght 2, tree_id 3, level 0, field2 "C2", field3 "C3">')
        self.assertEqual(repr(objects[3]), '<Model2D: id 4, parent None, field1 "D1", lft 1, rght 2, tree_id 4, level 0, field2 "D2", field3 "D3", field4 "D4">')

        # from a manual list
        objects = Model2A.objects.get_real_instances(list(qs))
        self.assertEqual(repr(objects[0]), '<Model2A: id 1, parent None, field1 "A1", lft 1, rght 2, tree_id 1, level 0>')
        self.assertEqual(repr(objects[1]), '<Model2B: id 2, parent None, field1 "B1", lft 1, rght 2, tree_id 2, level 0, field2 "B2">')
        self.assertEqual(repr(objects[2]), '<Model2C: id 3, parent None, field1 "C1", lft 1, rght 2, tree_id 3, level 0, field2 "C2", field3 "C3">')
        self.assertEqual(repr(objects[3]), '<Model2D: id 4, parent None, field1 "D1", lft 1, rght 2, tree_id 4, level 0, field2 "D2", field3 "D3", field4 "D4">')

    def test_translate_polymorphic_q_object(self):
        self.create_model2abcd()

        q = Model2A.translate_polymorphic_Q_object(Q(instance_of=Model2C))
        objects = Model2A.objects.filter(q)
        self.assertEqual(repr(objects[0]), '<Model2C: id 3, parent None, field1 "C1", lft 1, rght 2, tree_id 3, level 0, field2 "C2", field3 "C3">')
        self.assertEqual(repr(objects[1]), '<Model2D: id 4, parent None, field1 "D1", lft 1, rght 2, tree_id 4, level 0, field2 "D2", field3 "D3", field4 "D4">')

    def test_base_manager(self):
        def show_base_manager(model):
            return "{0} {1}".format(
                repr(type(model._base_manager)),
                repr(model._base_manager.model)
            )

        self.assertEqual(show_base_manager(PlainA), "<class 'django.db.models.manager.Manager'> <class 'polymorphic_tree.tests.models.PlainA'>")
        self.assertEqual(show_base_manager(PlainB), "<class 'django.db.models.manager.Manager'> <class 'polymorphic_tree.tests.models.PlainB'>")
        self.assertEqual(show_base_manager(PlainC), "<class 'django.db.models.manager.Manager'> <class 'polymorphic_tree.tests.models.PlainC'>")

        # Unlike standard polymorphic, the manager persists everywhere.
        # This makes sure that the features of MPTT are also available everywhere.
        self.assertEqual(show_base_manager(Model2A), "<class 'polymorphic_tree.managers.PolymorphicMPTTModelManager'> <class 'polymorphic_tree.tests.models.Model2A'>")
        self.assertEqual(show_base_manager(Model2B), "<class 'polymorphic_tree.managers.PolymorphicMPTTModelManager'> <class 'polymorphic_tree.tests.models.Model2B'>")
        self.assertEqual(show_base_manager(Model2C), "<class 'polymorphic_tree.managers.PolymorphicMPTTModelManager'> <class 'polymorphic_tree.tests.models.Model2C'>")

        self.assertEqual(show_base_manager(One2OneRelatingModel), "<class 'polymorphic_tree.managers.PolymorphicMPTTModelManager'> <class 'polymorphic_tree.tests.models.One2OneRelatingModel'>")
        self.assertEqual(show_base_manager(One2OneRelatingModelDerived), "<class 'polymorphic_tree.managers.PolymorphicMPTTModelManager'> <class 'polymorphic_tree.tests.models.One2OneRelatingModelDerived'>")

    def test_instance_default_manager(self):
        def show_default_manager(instance):
            return "{0} {1}".format(
                repr(type(instance._default_manager)),
                repr(instance._default_manager.model)
            )

        plain_a = PlainA(field1='C1')
        plain_b = PlainB(field2='C1')
        plain_c = PlainC(field3='C1')

        model_2a = Model2A(field1='C1')
        model_2b = Model2B(field2='C1')
        model_2c = Model2C(field3='C1')

        self.assertEqual(show_default_manager(plain_a), "<class 'django.db.models.manager.Manager'> <class 'polymorphic_tree.tests.models.PlainA'>")
        self.assertEqual(show_default_manager(plain_b), "<class 'django.db.models.manager.Manager'> <class 'polymorphic_tree.tests.models.PlainB'>")
        self.assertEqual(show_default_manager(plain_c), "<class 'django.db.models.manager.Manager'> <class 'polymorphic_tree.tests.models.PlainC'>")

        self.assertEqual(show_default_manager(model_2a), "<class 'polymorphic_tree.managers.PolymorphicMPTTModelManager'> <class 'polymorphic_tree.tests.models.Model2A'>")
        self.assertEqual(show_default_manager(model_2b), "<class 'polymorphic_tree.managers.PolymorphicMPTTModelManager'> <class 'polymorphic_tree.tests.models.Model2B'>")
        self.assertEqual(show_default_manager(model_2c), "<class 'polymorphic_tree.managers.PolymorphicMPTTModelManager'> <class 'polymorphic_tree.tests.models.Model2C'>")


class MPTTTests(TestCase):
    """
    Tests relating to tree structure of polymorphic objects

    TODO: port some tests from https://github.com/django-mptt/django-mptt/blob/master/tests/myapp/tests.py
    """

    def test_sibling_methods(self):
        """ https://github.com/edoburu/django-polymorphic-tree/issues/37 """
        root_node = Base.objects.create(field_b='root')
        sibling_a = Base.objects.create(field_b='first', parent=root_node)
        sibling_b = ModelX.objects.create(field_b='second', field_x='ModelX', parent=root_node)
        sibling_c = ModelY.objects.create(field_b='third', field_y='ModelY', parent=root_node)

        # sanity checks
        self.assertEqual(list(root_node.get_descendants()), [sibling_a, sibling_b, sibling_c])
        self.assertEqual(list(sibling_a.get_siblings()), [sibling_b, sibling_c])
        self.assertEqual(list(sibling_b.get_siblings()), [sibling_a, sibling_c])
        self.assertEqual(list(sibling_c.get_siblings()), [sibling_a, sibling_b])

        # When looking for siblings, it should be done from the base model,
        # not and not the child model type (which may not find all instances)
        self.assertEqual(sibling_a.get_previous_sibling(), None)
        self.assertEqual(sibling_a.get_next_sibling(), sibling_b)

        self.assertEqual(sibling_b.get_previous_sibling(), sibling_a)
        self.assertEqual(sibling_b.get_next_sibling(), sibling_c)

        self.assertEqual(sibling_c.get_previous_sibling(), sibling_b)
        self.assertEqual(sibling_c.get_next_sibling(), None)

    def test_get_ancestors(self):
        """ https://github.com/edoburu/django-polymorphic-tree/issues/32 """
        root_node = Base.objects.create(field_b='root')
        child = ModelX.objects.create(field_b='child', field_x='ModelX', parent=root_node)
        grandchild = ModelY.objects.create(field_b='grandchild', field_y='ModelY', parent=child)

        self.assertEqual(list(root_node.get_ancestors()), [])
        self.assertEqual(list(child.get_ancestors()), [root_node])
        self.assertEqual(list(grandchild.get_ancestors()), [root_node, child])

        self.assertEqual(list(root_node.get_ancestors(include_self=True)), [root_node])
        self.assertEqual(list(child.get_ancestors(include_self=True)), [root_node, child])
        self.assertEqual(list(grandchild.get_ancestors(include_self=True)), [root_node, child, grandchild])

        self.assertEqual(list(root_node.get_ancestors(ascending=True)), [])
        self.assertEqual(list(child.get_ancestors(ascending=True)), [root_node])
        self.assertEqual(list(grandchild.get_ancestors(ascending=True)), [child, root_node])

    def test_is_ancestor_of(self):
        root_node = Base.objects.create(field_b='root')
        child = ModelX.objects.create(field_b='child', field_x='ModelX', parent=root_node)
        grandchild = ModelY.objects.create(field_b='grandchild', field_y='ModelY', parent=child)

        self.assertTrue(root_node.is_ancestor_of(child))
        self.assertTrue(root_node.is_ancestor_of(grandchild))
        self.assertFalse(child.is_ancestor_of(root_node))
        self.assertTrue(child.is_ancestor_of(grandchild))
        self.assertFalse(grandchild.is_ancestor_of(child))
        self.assertFalse(grandchild.is_ancestor_of(root_node))

    def test_node_type_checking(self):
        root_node = Base.objects.create(field_b='root')
        child = ModelX.objects.create(field_b='child', field_x='ModelX', parent=root_node)
        grandchild = ModelY.objects.create(field_b='grandchild', field_y='ModelY', parent=child)

        self.assertFalse(root_node.is_child_node())
        self.assertFalse(root_node.is_leaf_node())
        self.assertTrue(root_node.is_root_node())

        self.assertTrue(child.is_child_node())
        self.assertFalse(child.is_leaf_node())
        self.assertFalse(child.is_root_node())

        self.assertTrue(grandchild.is_child_node())
        self.assertTrue(grandchild.is_leaf_node())
        self.assertFalse(grandchild.is_root_node())
