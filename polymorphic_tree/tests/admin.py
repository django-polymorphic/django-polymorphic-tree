from polymorphic_tree.admin import PolymorphicMPTTChildModelAdmin, PolymorphicMPTTParentModelAdmin
from polymorphic_tree.tests.models import ModelWithCustomParentName


class BaseChildAdmin(PolymorphicMPTTChildModelAdmin):
    """Test child admin"""

    GENERAL_FIELDSET = (
        None,
        {
            "fields": ("chief", "field5"),
        },
    )

    base_model = ModelWithCustomParentName
    base_fieldsets = (GENERAL_FIELDSET,)


class TreeNodeParentAdmin(PolymorphicMPTTParentModelAdmin):
    """Test parent admin"""

    base_model = ModelWithCustomParentName
    child_models = ((ModelWithCustomParentName, BaseChildAdmin),)

    list_display = (
        "field5",
        "actions_column",
    )
