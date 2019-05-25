from django.template.context_processors import csrf


def get_default_context(request, **kwargs):
    c = csrf(request)
    c.update(kwargs)
    return c