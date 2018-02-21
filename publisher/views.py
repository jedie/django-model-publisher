import logging

from django.views.generic import ListView
from django.views.generic.detail import DetailView

log = logging.getLogger(__name__)


class PublisherViewMixin:

    class Meta:
        abstract = True

    def get_queryset(self):
        return self.model.objects.visible()


class PublisherDetailView(PublisherViewMixin, DetailView):
    pass


class PublisherListView(PublisherViewMixin, ListView):
    pass
