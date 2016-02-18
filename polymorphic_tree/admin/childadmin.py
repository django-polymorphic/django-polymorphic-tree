from mptt.admin import MPTTModelAdmin
from mptt.forms import MPTTAdminForm
from polymorphic.admin import PolymorphicChildModelAdmin


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


    @property
    def change_form_template(self):
        # Insert template before default admin/polymorphic to have the tree in the breadcrumb
        templates = super(PolymorphicMPTTChildModelAdmin, self).change_form_template
        templates.insert(-2, "admin/polymorphic_tree/change_form.html")
        return templates

    @property
    def delete_confirmation_template(self):
        # Insert template before default admin/polymorphic to have the tree in the breadcrumb
        templates = super(PolymorphicMPTTChildModelAdmin, self).delete_confirmation_template
        templates.insert(-2, "admin/polymorphic_tree/delete_confirmation.html")
        return templates

    @property
    def object_history_template(self):
        # Insert template before default admin/polymorphic to have the tree in the breadcrumb
        templates = super(PolymorphicMPTTChildModelAdmin, self).object_history_template
        if isinstance(templates, list):  # allow pre django-polymorphic 0.9.1 to work without errors.
            templates.insert(-2, "admin/polymorphic_tree/object_history.html")
        return templates
