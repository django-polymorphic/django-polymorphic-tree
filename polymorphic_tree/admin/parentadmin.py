import json
from distutils.version import StrictVersion

from django.conf import settings
from django.contrib.admin import SimpleListFilter
from django.contrib.auth import get_permission_codename
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseRedirect
from django.urls import path, re_path, reverse
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from mptt.admin import MPTTModelAdmin
from mptt.exceptions import InvalidMove
from polymorphic.admin import PolymorphicModelChoiceForm, PolymorphicParentModelAdmin

from polymorphic_tree.models import PolymorphicMPTTModel


class NodeTypeChoiceForm(PolymorphicModelChoiceForm):
    type_label = _("Node type")


class NodeTypeListFilter(SimpleListFilter):
    parameter_name = "ct_id"
    title = _("node type")

    def lookups(self, request, model_admin):
        return model_admin.get_child_type_choices(request, "change")

    # Whoops: Django 1.6 didn't rename this one!
    def queryset(self, request, queryset):
        if self.value():
            queryset = queryset.filter(polymorphic_ctype_id=self.value())
        return queryset


class PolymorphicMPTTParentModelAdmin(PolymorphicParentModelAdmin, MPTTModelAdmin):
    """
    The parent admin, this renders the "list" page.
    It forwards the "edit" and "delete" views to the admin interface of the polymorphic models.

    The :func:`get_child_models` function or :attr:`child_models` attribute of the base class should still be implemented.
    """

    base_model = PolymorphicMPTTModel
    add_type_form = NodeTypeChoiceForm

    # Config list page:
    list_filter = (NodeTypeListFilter,)

    # TODO: disable the pagination in the admin, because it doesn't work with the current template code.
    # This is a workaround for https://github.com/edoburu/django-polymorphic-tree/issues/2 until
    # proper pagination code (or a different JavaScript frontend) is included to deal with the interrupted tree levels.
    list_per_page = 10000

    EMPTY_ACTION_ICON = '<span><img src="{STATIC_URL}polymorphic_tree/icons/blank.gif" width="16" height="16" alt="" class="{css_class}"/></span>'

    # ---- List code ----

    @property
    def change_list_template(self):
        templates = super().change_list_template
        templates.insert(-1, "admin/polymorphic_tree/change_list.html")  # Just before admin/change_list.html
        return templates

    # NOTE: the regular results table is replaced client-side with a jqTree list.
    # When making changes to the list, test both the JavaScript and non-JavaScript variant.
    # The jqTree variant still uses the server-side rendering for the columns.

    def actions_column(self, node):
        """
        An extra column to display action icons.
        Can be included in the :attr:`~django.contrib.admin.ModelAdmin.list_display` attribute.
        """
        return " ".join(self.get_action_icons(node))

    actions_column.allow_tags = True
    actions_column.short_description = _("Actions")

    def get_action_icons(self, node):
        """
        Return a list of all action icons in the :func:`actions_column`.
        """
        actions = []
        if node.can_have_children:
            actions.append(
                '<a href="add/?{parent_attr}={id}" title="{title}" class="add-child-object">'
                '<img src="{static}polymorphic_tree/icons/page_new.gif" width="16" height="16" alt="{title}" /></a>'.format(
                    parent_attr=self.model._mptt_meta.parent_attr,
                    id=node.pk,
                    title=_("Add sub node"),
                    static=settings.STATIC_URL,
                )
            )
        else:
            actions.append(self.EMPTY_ACTION_ICON.format(STATIC_URL=settings.STATIC_URL, css_class="add-child-object"))

        if self.can_preview_object(node):
            actions.append(
                '<a href="{url}" title="{title}" target="_blank">'
                '<img src="{static}polymorphic_tree/icons/world.gif" width="16" height="16" alt="{title}" /></a>'.format(
                    url=node.get_absolute_url(), title=_("View on site"), static=settings.STATIC_URL
                )
            )

        # The is_first_sibling and is_last_sibling is quite heavy. Instead rely on CSS to hide the arrows.
        move_up = f'<a href="{node.pk}/move_up/" class="move-up">\u2191</a>'
        move_down = f'<a href="{node.pk}/move_down/" class="move-down">\u2193</a>'
        actions.append(f'<span class="no-js">{move_up}{move_down}</span>')
        return actions

    def can_preview_object(self, node):
        """
        Define whether a node can be previewed.
        """
        return hasattr(node, "get_absolute_url")

    # ---- Custom views ----

    def get_urls(self):
        """
        Add custom URLs for moving nodes.
        """
        base_urls = super().get_urls()
        info = _get_opt(self.model)
        extra_urls = [
            path(
                "api/node-moved/",
                self.admin_site.admin_view(self.api_node_moved_view),
                name="{}_{}_moved".format(*info),
            ),
            re_path(r"^(\d+)/move_up/$", self.admin_site.admin_view(self.move_up_view)),
            re_path(r"^(\d+)/move_down/$", self.admin_site.admin_view(self.move_down_view)),
        ]
        return extra_urls + base_urls

    @property
    def api_node_moved_view_url(self):
        # Provided for result list template
        info = _get_opt(self.model)
        return reverse("admin:{}_{}_moved".format(*info), current_app=self.admin_site.name)

    @transaction.atomic
    def api_node_moved_view(self, request):
        """
        Update the position of a node, from a API request.
        """
        try:
            moved_id = _get_pk_value(request.POST["moved_id"])
            target_id = _get_pk_value(request.POST["target_id"])
            position = request.POST["position"]

            if request.POST.get("previous_parent_id"):
                previous_parent_id = _get_pk_value(request.POST["previous_parent_id"])
            else:
                previous_parent_id = None

            # Not using .non_polymorphic() so all models are downcasted to the derived model.
            # This causes the signal below to be emitted from the proper class as well.
            moved = self.model.objects.get(pk=moved_id)
            target = self.model.objects.get(pk=target_id)
        except (ValueError, KeyError) as e:
            return HttpResponseBadRequest(
                json.dumps({"action": "foundbug", "error": str(e[0])}), content_type="application/json"
            )
        except self.model.DoesNotExist as e:
            return HttpResponseNotFound(
                json.dumps({"action": "reload", "error": str(e[0])}), content_type="application/json"
            )

        if not request.user.has_perm(
            "{}.{}".format(moved._meta.app_label, get_permission_codename("change", moved._meta))
        ):
            return HttpResponse(
                json.dumps(
                    {
                        "action": "reject",
                        "moved_id": moved_id,
                        "error": gettext("You do not have permission to move this node."),
                    }
                ),
                content_type="application/json",
                status=409,
            )

        # Compare on strings to support UUID fields.
        parent_attr_id = f"{moved._mptt_meta.parent_attr}_id"
        if str(getattr(moved, parent_attr_id)) != str(previous_parent_id):
            return HttpResponse(
                json.dumps({"action": "reload", "error": "Client seems to be out-of-sync, please reload!"}),
                content_type="application/json",
                status=409,
            )

        mptt_position = {
            "inside": "first-child",
            "before": "left",
            "after": "right",
        }[position]
        try:
            moved.move_to(target, mptt_position)
        except ValidationError as e:
            return HttpResponse(
                json.dumps({"action": "reject", "moved_id": moved_id, "error": "\n".join(e.messages)}),
                content_type="application/json",
                status=409,
            )  # Conflict
        except InvalidMove as e:
            return HttpResponse(
                json.dumps({"action": "reject", "moved_id": moved_id, "error": str(e)}),
                content_type="application/json",
                status=409,
            )

        # Some packages depend on calling .save() or post_save signal after updating a model.
        # This is required by django-fluent-pages for example to update the URL caches.
        moved.save()

        # Report back to client.
        return HttpResponse(
            json.dumps(
                {
                    "action": "success",
                    "error": None,
                    "moved_id": moved_id,
                    "action_column": self.actions_column(moved),
                }
            ),
            content_type="application/json",
        )

    def move_up_view(self, request, object_id):
        node = self.model.objects.get(pk=object_id)

        if node is not None:
            previous_sibling_category = node.get_previous_sibling()
            if previous_sibling_category is not None:
                node.move_to(previous_sibling_category, position="left")

        return HttpResponseRedirect("../../")

    def move_down_view(self, request, object_id):
        node = self.model.objects.get(pk=object_id)

        if node is not None:
            next_sibling_category = node.get_next_sibling()
            if next_sibling_category is not None:
                node.move_to(next_sibling_category, position="right")

        return HttpResponseRedirect("../../")


def _get_opt(model):
    try:
        return model._meta.app_label, model._meta.model_name  # Django 1.7 format
    except AttributeError:
        return model._meta.app_label, model._meta.module_name


def _get_pk_value(text):
    try:
        return int(text)
    except ValueError:
        return text  # Allow uuid fields
