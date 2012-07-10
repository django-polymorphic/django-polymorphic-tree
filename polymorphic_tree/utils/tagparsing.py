from django.template.base import TemplateSyntaxError, Token
import re

kwarg_re = re.compile('^(?P<name>\w+)=')

def parse_token_kwargs(parser, token, compile_args=False, compile_kwargs=False, allowed_kwargs=None):
    """
    Allow the template tag arguments to be like a normal Python function, with *args and **kwargs.
    """
    if isinstance(token, Token):
        bits = token.split_contents()
    else:
        bits = token

    expect_kwarg = False
    args = []
    kwargs = {}
    prev_bit = None

    for bit in bits[1::]:
        match = kwarg_re.match(bit)
        if match:
            expect_kwarg = True
            (name, expr) = bit.split('=', 2)
            kwargs[name] = parser.compile_filter(expr) if compile_args else expr
        else:
            if expect_kwarg:
                raise TemplateSyntaxError("{0} tag may not have a non-keyword argument ({1}) after a keyword argument ({2}).".format(bits[0], bit, prev_bit))
            args.append(parser.compile_filter(bit) if compile_kwargs else bit)

        prev_bit = bit

    # Validate the allowed arguments, to make things easier for template developers
    if allowed_kwargs is not None:
        for name in kwargs:
            if name not in allowed_kwargs:
                raise AttributeError("The option %s=... cannot be used in '%s'.\nPossible options are: %s." % (name, bits[0], ", ".join(allowed_kwargs)))

    return args, kwargs
