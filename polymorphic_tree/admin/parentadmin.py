import json, django
from future.builtins import str, int
from distutils.version import StrictVersion
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseNotFound, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicModelChoiceForm
from polymorphic_tree.models import PolymorphicMPTTModel
from mptt.admin import MPTTModelAdmin

try:
    from polymorphic.__version__ import __version__ as polymorphic_version  # pre 0.8 used a __version__.py
except ImportError:
    from polymorphic import __version__ as polymorphic_version

try:
    # Django 1.6 requires this
    from django.conf.urls import url
except ImportError:
    # Django 1.3 compatibility
    from django.conf.urls.defaults import url


try:
    transaction_atomic = transaction.atomic
except AttributeError:
    transaction_atomic = transaction.commit_on_success


class NodeTypeChoiceForm(PolymorphicModelChoiceForm):
    type_label = _("Node type")


try:
    from django.contrib.admin import SimpleListFilter
except ImportError:
    extra_list_filters = ()
else:
    # Django 1.4+:
    class NodeTypeListFilter(SimpleListFilter):
        parameter_name = 'ct_id'
        title = _('node type')

        def lookups(self, request, model_admin):
            if StrictVersion(polymorphic_version) >= StrictVersion('0.6'):
                return model_admin.get_child_type_choices(request, 'change')
            return model_admin.get_child_type_choices()

        # Whoops: Django 1.6 didn't rename this one!
        def queryset(self, request, queryset):
            if self.value():
                queryset = queryset.filter(polymorphic_ctype_id=self.value())
            return queryset

    extra_list_filters = (NodeTypeListFilter,)


class PolymorphicMPTTParentModelAdmin(PolymorphicParentModelAdmin, MPTTModelAdmin):
    """
    The parent admin, this renders the "list" page.
    It forwards the "edit" and "delete" views to the admin interface of the polymorphic models.

    The :func:`get_child_models` function or :attr:`child_models` attribute of the base class should still be implemented.
    """
    base_model = PolymorphicMPTTModel
    add_type_form = NodeTypeChoiceForm

    # Config list page:
    list_filter = extra_list_filters

    # TODO: disable the pagination in the admin, because it doesn't work with the current template code.
    # This is a workaround for https://github.com/edoburu/django-polymorphic-tree/issues/2 until
    # proper pagination code (or a different JavaScript frontend) is included to deal with the interrupted tree levels.
    list_per_page = 10000

    EMPTY_ACTION_ICON = u'<span><img src="{STATIC_URL}polymorphic_tree/icons/blank.gif" width="16" height="16" alt="" class="{css_class}"/></span>'

    # ---- List code ----

    @property
    def change_list_template(self):
        templates = super(PolymorphicMPTTParentModelAdmin, self).change_list_template
        templates.insert(-1, 'admin/polymorphic_tree/change_list.html')  # Just before admin/change_list.html
        return templates


    # NOTE: the regular results table is replaced client-side with a jqTree list.
    # When making changes to the list, test both the JavaScript and non-JavaScript variant.
    # The jqTree variant still uses the server-side rendering for the columns.


    def actions_column(self, node):
        """
        An extra column to display action icons.
        Can be included in the :attr:`~django.contrib.admin.ModelAdmin.list_display` attribute.
        """
        return u' '.join(self.get_action_icons(node))

    actions_column.allow_tags = True
    actions_column.short_description = _('Actions')


    def get_action_icons(self, node):
        """
        Return a list of all action icons in the :func:`actions_column`.
        """
        actions = []
        if self.can_have_children(node):
            actions.append(
                u'<a href="add/?{parent_attr}={id}" title="{title}" class="add-child-object"><img src="{static}polymorphic_tree/icons/page_new.gif" width="16" height="16" alt="{title}" /></a>'.format(
                    parent_attr=self.model._mptt_meta.parent_attr, id=node.pk, title=_('Add sub node'), static=settings.STATIC_URL)
            )
        else:
            actions.append(self.EMPTY_ACTION_ICON.format(STATIC_URL=settings.STATIC_URL, css_class='add-child-object'))

        if self.can_preview_object(node):
            actions.append(
                u'<a href="{url}" title="{title}" target="_blank"><img src="{static}polymorphic_tree/icons/world.gif" width="16" height="16" alt="{title}" /></a>'.format(
                    url=node.get_absolute_url(), title=_('View on site'), static=settings.STATIC_URL)
            )

        # The is_first_sibling and is_last_sibling is quite heavy. Instead rely on CSS to hide the arrows.
        move_up = u'<a href="{0}/move_up/" class="move-up">\u2191</a>'.format(node.pk)
        move_down = u'<a href="{0}/move_down/" class="move-down">\u2193</a>'.format(node.pk)
        actions.append(u'<span class="no-js">{0}{1}</span>'.format(move_up, move_down))
        return actions


    def can_preview_object(self, node):
        """
        Define whether a node can be previewed.
        """
        return hasattr(node, 'get_absolute_url')


    def can_have_children(self, node):
        """
        Define whether a node can have children.
        """
        # Allow can_have_children to be either to be a property on the base class that always works.
        if not node.can_have_children:
            return False

        # or a static variable declared on the class (avoids need for downcasted models).
        NodeClass = node.get_real_instance_class()
        return bool(NodeClass.can_have_children)



    # ---- Custom views ----

    def get_urls(self):
        """
        Add custom URLs for moving nodes.
        """
        base_urls = super(PolymorphicMPTTParentModelAdmin, self).get_urls()
        info = _get_opt(self.model)
        extra_urls = [
            url(r'^api/node-moved/$', self.admin_site.admin_view(self.api_node_moved_view), name='{0}_{1}_moved'.format(*info)),
            url(r'^(\d+)/move_up/$', self.admin_site.admin_view(self.move_up_view)),
            url(r'^(\d+)/move_down/$', self.admin_site.admin_view(self.move_down_view)),
        ]
        return extra_urls + base_urls


    @property
    def api_node_moved_view_url(self):
        # Provided for result list template
        info = _get_opt(self.model)
        return reverse('admin:{0}_{1}_moved'.format(*info), current_app=self.admin_site.name)


    @transaction_atomic
    def api_node_moved_view(self, request):
        """
        Update the position of a node, from a API request.
        """
        try:
            moved_id = int(request.POST['moved_id'])
            target_id = int(request.POST['target_id'])
            position = request.POST['position']
            previous_parent_id = int(request.POST['previous_parent_id']) or None

            # Not using .non_polymorphic() so all models are downcasted to the derived model.
            # This causes the signal below to be emitted from the proper class as well.
            moved = self.model.objects.get(pk=moved_id)
            target = self.model.objects.get(pk=target_id)
        except (ValueError, KeyError) as e:
            return HttpResponseBadRequest(json.dumps({'action': 'foundbug', 'error': str(e[0])}), content_type='application/json')
        except self.model.DoesNotExist as e:
            return HttpResponseNotFound(json.dumps({'action': 'reload', 'error': str(e[0])}), content_type='application/json')

        if not self.can_have_children(target) and position == 'inside':
            return HttpResponse(json.dumps({
                'action': 'reject',
                'moved_id': moved_id,
                'error': _(u'Cannot place \u2018{0}\u2019 below \u2018{1}\u2019; a {2} does not allow children!').format(moved, target, target._meta.verbose_name)
            }), content_type='application/json', status=409)  # Conflict
        if moved.parent_id != previous_parent_id:
            return HttpResponse(json.dumps({
                'action': 'reload',
                'error': 'Client seems to be out-of-sync, please reload!'
            }), content_type='application/json', status=409)

        # TODO: with granular user permissions, check if user is allowed to edit both pages.

        mptt_position = {
            'inside': 'first-child',
            'before': 'left',
            'after': 'right',
        }[position]
        moved.move_to(target, mptt_position)

        # Some packages depend on calling .save() or post_save signal after updating a model.
        # This is required by django-fluent-pages for example to update the URL caches.
        moved.save()

        # Report back to client.
        return HttpResponse(json.dumps({
            'action': 'success',
            'error': None,
            'moved_id': moved_id,
            'action_column': self.actions_column(moved),
        }), content_type='application/json')


    def move_up_view(self, request, object_id):
        node = self.model.objects.get(pk=object_id)

        if node is not None:
            previous_sibling_category = node.get_previous_sibling()
            if previous_sibling_category is not None:
                node.move_to(previous_sibling_category, position='left')

        return HttpResponseRedirect('../../')


    def move_down_view(self, request, object_id):
        node = self.model.objects.get(pk=object_id)

        if node is not None:
            next_sibling_category = node.get_next_sibling()
            if next_sibling_category is not None:
                node.move_to(next_sibling_category, position='right')

        return HttpResponseRedirect('../../')


def _get_opt(model):
    try:
        return model._meta.app_label, model._meta.model_name  # Django 1.7 format
    except AttributeError:
        return model._meta.app_label, model._meta.module_name

