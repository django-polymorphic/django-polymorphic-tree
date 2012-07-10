from django.utils.functional import lazy
from mptt.admin import MPTTModelAdmin
from mptt.forms import MPTTAdminForm
from polymorphic_tree.utils.polymorphicadmin import PolymorphicChildModelAdmin
from polymorphic_tree.models import PolymorphicMPTTModel


class PolymorpicMPTTAdminForm(MPTTAdminForm):
    pass


class PolymorphicMPTTChildModelAdmin(PolymorphicChildModelAdmin, MPTTModelAdmin):
    """
    The internal machinery
    The admin screen for the ``PolymorphicMPTTModel`` objects.
    """
    base_model = PolymorphicMPTTModel
    base_form = PolymorpicMPTTAdminForm
    base_fieldsets = None


    # NOTE: list page is configured in PolymorphicMPTTParentModelAdmin
    # as that class is used for the real admin screen in the edit/delete view.
    # This class is only a base class for the custom node type plugins.


    # ---- Pass parent_object to templates ----

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        # Get parent object for breadcrumb
        parent_object = None
        parent_id = request.REQUEST.get('parent')
        if add and parent_id:
            assert not self.base_model._meta.abstract, "should define {0}.base_model".format(self.__class__.__name__)
            parent_object = self.base_model.objects.get(pk=int(parent_id))  # is polymorphic
        elif change:
            parent_object = obj.parent

        # Pass parent object to the view.
        # Also allows to improve the breadcrumb for example
        context.update({
            'parent_object': parent_object,
            'parent_breadcrumb': lazy(lambda: list(parent_object.get_ancestors()) + [parent_object], list)() if parent_object else [],
        })

        return super(PolymorphicMPTTChildModelAdmin, self).render_change_form(request, context, add=add, change=change, form_url=form_url, obj=obj)


    def delete_view(self, request, object_id, context=None):
        # Get parent object for breadcrumb
        parent_object = None
        try:
            assert not self.base_model._meta.abstract, "should define {0}.base_model".format(self.__class__.__name__)
            parent_pk = self.base_model.objects.non_polymorphic().values('parent').filter(pk=int(object_id))
            parent_object = self.base_model.objects.get(pk=parent_pk)
        except PolymorphicMPTTModel.DoesNotExist:
            pass

        # Pass parent object to the view.
        # Also allows to improve the breadcrumb for example
        extra_context = {
            'parent_object': parent_object,
            'parent_breadcrumb': lazy(lambda: list(parent_object.get_ancestors()) + [parent_object], list)(),
        }
        extra_context.update(context or {})

        return super(PolymorphicMPTTChildModelAdmin, self).delete_view(request, object_id, extra_context)
