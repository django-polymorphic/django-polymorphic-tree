import sys
from unittest import TestCase
from unittest.mock import MagicMock

from django.contrib.admin import AdminSite

import polymorphic_tree.templatetags.stylable_admin_list  # noqa (only for import testing)
from polymorphic_tree.admin.parentadmin import get_permission_codename
from polymorphic_tree.tests.admin import TreeNodeParentAdmin
from polymorphic_tree.tests.models import Model2A, ModelWithCustomParentName, ModelWithInvalidMove, ModelWithValidation


class PolymorphicAdminTests(TestCase):
    """Tests for admin"""

    def setUp(self):
        self.parent = ModelWithCustomParentName.objects.create(field5="parent")
        self.child1 = ModelWithCustomParentName.objects.create(field5="child1", chief=self.parent)
        self.child2 = ModelWithCustomParentName.objects.create(field5="child2", chief=self.parent)
        self.parent_admin = TreeNodeParentAdmin(ModelWithCustomParentName, AdminSite())

        self.parent_with_validation = ModelWithValidation.objects.create(field6="parent")
        self.child1_with_validation = ModelWithValidation.objects.create(
            field6="child1", parent=self.parent_with_validation
        )
        self.child2_with_validation = ModelWithValidation.objects.create(
            field6="child2", parent=self.parent_with_validation
        )

        self.parent_admin_with_validation = TreeNodeParentAdmin(ModelWithValidation, AdminSite())

        self.parent_invalid_move = ModelWithInvalidMove.objects.create(field7="parent")
        self.child1_invalid_move = ModelWithInvalidMove.objects.create(field7="child1", parent=self.parent_invalid_move)
        self.child2_invalid_move = ModelWithInvalidMove.objects.create(field7="child2", parent=self.parent_invalid_move)

        self.parent_admin_invalid_move = TreeNodeParentAdmin(ModelWithInvalidMove, AdminSite())

    def test_make_child2_child_child1(self):
        """Make ``self.child2`` child of ``self.child1``"""
        request = MagicMock()
        request.POST = {
            "moved_id": self.child2.id,
            "target_id": self.child1.id,
            "previous_parent_id": self.parent.id,
            "position": "inside",
        }
        self.parent_admin.api_node_moved_view(request)
        # Analog of self.child2.refresh_from_db()
        # This hack used for django 1.7 support
        self.child2 = ModelWithCustomParentName.objects.get(pk=self.child2.pk)
        self.assertEqual(self.child2.chief, self.child1)

    def test_validation_error(self):
        """Ensure that if move can't be performed due validation error, move
        can't be performed and json error returned
        """
        request = MagicMock()
        request.POST = {
            "moved_id": self.child2_with_validation.id,
            "target_id": self.child1_with_validation.id,
            "previous_parent_id": self.parent_with_validation.id,
            "position": "inside",
        }

        resp = self.parent_admin_with_validation.api_node_moved_view(request)

        self.assertEqual(resp.status_code, 409)

    def test_invalid_move(self):
        """Ensure that if move can't be performed due validation error, move
        can't be performed and json error returned
        """
        request = MagicMock()
        request.POST = {
            "moved_id": self.child2_invalid_move.id,
            "target_id": self.child1_invalid_move.id,
            "previous_parent_id": self.parent_invalid_move.id,
            "position": "inside",
        }

        resp = self.parent_admin_invalid_move.api_node_moved_view(request)

        self.assertEqual(resp.status_code, 409)

    def test_get_permission_codename(self):
        # This is to test whether our function works in older Django versions.
        self.assertEqual(get_permission_codename("change", Model2A._meta), "change_model2a")
