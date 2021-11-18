from django.contrib import admin

from polymorphic_tree.admin import PolymorphicMPTTChildModelAdmin, PolymorphicMPTTParentModelAdmin

from . import models

# The common admin functionality for all derived models:


class BaseChildAdmin(PolymorphicMPTTChildModelAdmin):
    GENERAL_FIELDSET = (
        None,
        {
            "fields": ("parent", "title"),
        },
    )

    base_model = models.BaseTreeNode
    base_fieldsets = (GENERAL_FIELDSET,)


# Optionally some custom admin code


class TextNodeAdmin(BaseChildAdmin):
    pass


# Create the parent admin that combines it all:


class TreeNodeParentAdmin(PolymorphicMPTTParentModelAdmin):
    base_model = models.BaseTreeNode
    child_models = (
        (models.CategoryNode, BaseChildAdmin),
        (models.TextNode, TextNodeAdmin),  # custom admin allows custom edit/delete view.
        (models.ImageNode, BaseChildAdmin),
    )

    list_display = (
        "title",
        "actions_column",
    )


admin.site.register(models.BaseTreeNode, TreeNodeParentAdmin)
