
"""
    created 2017-2018 by Jens Diemer <ya-publisher@jensdiemer.de>
"""

import logging

from cms.utils import get_language_from_request

from menus.utils import set_language_changer
from parler.views import TranslatableSlugMixin

from publisher_cms.views import PublisherCmsDetailView, PublisherCmsListView
from publisher_test_project.publisher_list_app.constants import LIST_TOOLBAR_KEY, LIST_TOOLBAR_VERBOSE_NAME
from publisher_test_project.publisher_list_app.models import PublisherItem

log = logging.getLogger(__name__)


class PublisherItemListView(PublisherCmsListView):
    model = PublisherItem
    template_name = 'list_app/list.html'


class PublisherItemDetailView(TranslatableSlugMixin, PublisherCmsDetailView):
    model = PublisherItem
    template_name = 'list_app/detail.html'

    toolbar_key = LIST_TOOLBAR_KEY
    toolbar_verbose_name = LIST_TOOLBAR_VERBOSE_NAME

    def get(self, request, *args, **kwargs):
        self.language = get_language_from_request(request)
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        instance = super().get_object(queryset=queryset)

        # Translate the slug while changing the language:
        set_language_changer(self.request, instance.get_absolute_url)

        self.extend_toolbar(publisher_instance=instance)

        return instance
