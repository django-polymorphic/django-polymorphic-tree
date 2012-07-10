from mptt.admin import MPTTModelAdmin
from mptt.forms import MPTTAdminForm
from polymorphic_tree.utils.polymorphicadmin import PolymorphicChildModelAdmin


class PolymorpicMPTTAdminForm(MPTTAdminForm):
    pass


class PolymorphicMPTTChildModelAdmin(PolymorphicChildModelAdmin, MPTTModelAdmin):
    """
    The internal machinery
    The admin screen for the ``PolymorphicMPTTModel`` objects.
    """
    base_model = None
    base_form = PolymorpicMPTTAdminForm
    base_fieldsets = None

    # NOTE: list page is configured in PolymorphicMPTTParentModelAdmin
    # as that class is used for the real admin screen in the edit/delete view.
    # This class is only a base class for the custom node type plugins.
