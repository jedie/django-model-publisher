from django.urls import reverse

from publisher.app_settings import ADMIN_NAMESPACE


def admin_url(obj, name):
    """
    Helper used in models to generate admin urls
    """
    opts = obj._meta
    viewname = '%s:%s_%s_%s' % (ADMIN_NAMESPACE, opts.app_label, opts.model_name, name)
    url = reverse(viewname, args=(obj.pk,))
    return url
