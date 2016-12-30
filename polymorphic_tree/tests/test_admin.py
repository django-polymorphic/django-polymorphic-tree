from unittest import TestCase
from unittest.mock import MagicMock

from django.contrib.admin import AdminSite

from polymorphic_tree.tests.admin import TreeNodeParentAdmin
from polymorphic_tree.tests.models import ModelWithCustomParentName


class PolymorphicAdminTests(TestCase):
    """Tests for admin"""

    def setUp(self):
        self.parent = ModelWithCustomParentName.objects.create(field5='parent')
        self.child1 = ModelWithCustomParentName.objects.create(
            field5='child1',
            chief=self.parent
        )
        self.child2 = ModelWithCustomParentName.objects.create(
            field5='child2',
            chief=self.parent
        )
        self.parent_admin = TreeNodeParentAdmin(ModelWithCustomParentName,
                                                AdminSite())

    def test_make_child2_child_child1(self):
        """Make ``self.child2`` child of ``self.child1``"""
        request = MagicMock()
        request.POST = {
            'moved_id': self.child2.id,
            'target_id': self.child1.id,
            'previous_parent_id': self.parent.id,
            'position': 'inside'
        }
        self.parent_admin.api_node_moved_view(request)
        self.child2.refresh_from_db()
        self.assertEqual(self.child2.chief, self.child1)