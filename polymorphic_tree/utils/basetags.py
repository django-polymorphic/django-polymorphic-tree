from django.template import Node, Context, TemplateSyntaxError
from django.template.loader import get_template
from polymorphic_tree.utils.tagparsing import parse_token_kwargs


class ExtensibleInclusionNode(Node):
    """
    Base class to render a template tag with a template.

    This class allows more flexibility then Django's default :func:`django.template.Library.inclusion_tag` decorator.
    It allows specify the template name via:
    - a static ``template_name`` property.
    - a ``get_template_name()`` method
    - a 'template' kwarg in the HTML.
    """
    template_name = None
    allowed_kwargs = ('template',)
    min_args = 0
    max_args = 0


    def __init__(self, tagname, *args, **kwargs):
        self.tagname = tagname
        self.args = args
        self.kwargs = kwargs


    @classmethod
    def parse(cls, parser, token):
        tagname = token.contents.split(' ', 2)[0]
        args, kwargs = parse_token_kwargs(parser, token, True, True, cls.allowed_kwargs)
        cls.parse_args(tagname, *args)
        return cls(tagname, *args, **kwargs)


    @classmethod
    def parse_args(cls, tagname, *args):
        """
        Split the arguments in individual properties, if needed.
        """
        if len(args) < cls.min_args:
            if cls.min_args == 1:
                raise TemplateSyntaxError("'{0}' tag requires at least {1} argument".format(tagname))
            else:
                raise TemplateSyntaxError("'{0}' tag requires at least {1} arguments".format(tagname))

        if len(args) > cls.max_args:
            if cls.max_args == 0:
                raise TemplateSyntaxError("'{0}' tag only allows keywords arguments, for example template=\"...\".".format(tagname))
            elif cls.max_args == 1:
                raise TemplateSyntaxError("'{0}' tag only allows {1} argument.".format(tagname, self.max_args))
            else:
                raise TemplateSyntaxError("'{0}' tag only allows {1} arguments.".format(tagname, self.max_args))


    def render(self, context):
        # Resolve token kwargs
        parsed_args = [expr.resolve(context) for expr in self.args]
        parsed_kwargs = dict([(name, expr.resolve(context)) for name, expr in self.kwargs.iteritems()])

        # Get template nodes, and cache it.
        # Note that self.nodelist is special in the Node baseclass.
        if not getattr(self, 'nodelist', None):
            tpl = get_template(self.get_template_name(*parsed_args, **parsed_kwargs))
            self.nodelist = tpl.nodelist

        # Render the node
        # Pass csrf token for same reasons as @register.inclusion_tag does.
        data = self.get_context_data(context, *parsed_args, **parsed_kwargs)
        new_context = Context(data, autoescape=context.autoescape)

        csrf_token = context.get('csrf_token', None)
        if csrf_token is not None:
            new_context['csrf_token'] = csrf_token

        return self.nodelist.render(new_context)


    def get_template_name(self, *tag_args, **tag_kwargs):
        """
        Get the template name, by default using
        """
        return tag_kwargs.get('template', self.template_name)


    def get_context_data(self, parent_context, *tag_args, **tag_kwargs):
        """
        Return the context data for the included template.
        """
        raise NotImplementedError()
