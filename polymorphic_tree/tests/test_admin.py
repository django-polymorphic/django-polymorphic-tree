from django.test import TestCase
from polymorphic_tree.admin.parentadmin import get_permission_codename
from polymorphic_tree.tests.models import Model2A


class AdminTestCase(TestCase):
    def test_get_permission_codename(self):
        # This is to test whether our function works in older Django versions.
        self.assertEqual(get_permission_codename('change', Model2A._meta), 'change_model2a')
