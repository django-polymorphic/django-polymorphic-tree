from django.contrib.admin.views.main import ChangeList
from django.contrib.contenttypes.models import ContentType
from django.template import Library, Node, TemplateSyntaxError, Variable
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from mptt.templatetags.mptt_tags import cache_tree_children
from polymorphic_tree.templatetags.stylable_admin_list import stylable_column_repr

register = Library()


class BreadcrumbScope(Node):
    def __init__(self, base_opts, nodelist):
        self.base_opts = base_opts
        self.nodelist = nodelist   # Note, takes advantage of Node.child_nodelists

    @classmethod
    def parse(cls, parser, token):
        bits = token.split_contents()
        if len(bits) == 2:
            (tagname, base_opts) = bits
            base_opts = parser.compile_filter(base_opts)
            nodelist = parser.parse(('endbreadcrumb_scope',))
            parser.delete_first_token()

            return cls(
                base_opts=base_opts,
                nodelist=nodelist
            )
        else:
            raise TemplateSyntaxError("{0} tag expects 1 argument".format(token.contents[0]))


    def render(self, context):
        # app_label is really hard to overwrite in the standard Django ModelAdmin.
        # To insert it in the template, the entire render_change_form() and delete_view() have to copied and adjusted.
        # Instead, overwrite them here.
        base_opts = self.base_opts.resolve(context)
        new_vars = {}
        if base_opts and not isinstance(base_opts, basestring):
            new_vars = {
                'app_label': base_opts.app_label,  # What this is all about
                'opts': base_opts,
            }

        d = context.push()
        d.update(new_vars)
        html = self.nodelist.render(context)
        context.pop()
        return html


@register.tag
def breadcrumb_scope(parser, token):
    return BreadcrumbScope.parse(parser, token)


@register.filter
def real_model_name(node):
    # Allow upcasted model to work.
    # node.get_real_instance_class().__name__ would also work
    return ContentType.objects.get_for_id(node.polymorphic_ctype_id).model


@register.filter
def mptt_breadcrumb(node):
    """
    Return a breadcrumb of nodes, for the admin breadcrumb
    """
    if node is None:
        return []
    else:
        return list(node.get_ancestors())


class AdminListRecurseTreeNode(Node):
    def __init__(self, template_nodes, cl_var):
        self.template_nodes = template_nodes
        self.cl_var = cl_var

    @classmethod
    def parse(cls, parser, token):
        bits = token.contents.split()
        if len(bits) != 2:
            raise TemplateSyntaxError('%s tag requires an admin ChangeList' % bits[0])

        cl_var = Variable(bits[1])

        template_nodes = parser.parse(('endadminlist_recursetree',))
        parser.delete_first_token()
        return cls(template_nodes, cl_var)

    def _render_node(self, context, cl, node):
        bits = []
        context.push()

        # Render children to add to parent later
        for child in node.get_children():
            bits.append(self._render_node(context, cl, child))

        columns = self._get_column_repr(cl, node)  # list(tuple(name, html), ..)
        first_real_column = (col for col in columns if col[0] != 'action_checkbox').next()

        context['columns'] = columns
        context['other_columns'] = [col for col in columns if col[0] not in ('action_checkbox', first_real_column[0])]
        context['first_column'] = first_real_column[1]
        context['named_columns'] = dict(columns)
        context['node'] = node
        context['change_url'] = cl.url_for_result(node)
        context['children'] = mark_safe(u''.join(bits))

        # Render
        rendered = self.template_nodes.render(context)
        context.pop()
        return rendered

    def render(self, context):
        cl = self.cl_var.resolve(context)
        assert isinstance(cl, ChangeList), "cl variable should be an admin ChangeList"  # Also assists PyCharm
        roots = cache_tree_children(cl.result_list)
        bits = [self._render_node(context, cl, node) for node in roots]
        return ''.join(bits)

    def _get_column_repr(self, cl, node):
        columns = []
        for field_name in cl.list_display:
            html, row_class_ = stylable_column_repr(cl, node, field_name)
            columns.append((field_name, html))
        return columns


@register.tag
def adminlist_recursetree(parser, token):
    """
    Very similar to the mptt recursetree, except that it also returns the styled admin code.
    """
    return AdminListRecurseTreeNode.parse(parser, token)
