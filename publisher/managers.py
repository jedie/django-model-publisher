import logging

from django.db import models
from django.db.models import Q
from django.utils import timezone

from .middleware import get_draft_status
from .signal_handlers import publisher_post_save, publisher_pre_delete

log = logging.getLogger(__name__)


class PublisherQuerySet(models.QuerySet):
    def drafts(self):
        from .models import PublisherModelBase
        return self.filter(publisher_is_draft=PublisherModelBase.STATE_DRAFT)

    def published(self):
        """
        Note: will ignore start/end date!
        Use self.visible() to get all publicly accessible entries.
        """
        from .models import PublisherModelBase
        return self.filter(
            publisher_is_draft=PublisherModelBase.STATE_PUBLISHED,
        )

    def visible(self):
        """
        Filter all publicly accessible entries.
        """
        from .models import PublisherModelBase
        return self.filter(
            Q(publication_start_date__isnull=True) | Q(publication_start_date__lte=timezone.now()),
            Q(publication_end_date__isnull=True) | Q(publication_end_date__gt=timezone.now()),
            publisher_is_draft=PublisherModelBase.STATE_PUBLISHED,
        )


class BasePublisherManager(models.Manager):
    def get_queryset(self):
        return PublisherQuerySet(self.model, using=self._db)

    def contribute_to_class(self, model, name):
        super(BasePublisherManager, self).contribute_to_class(model, name)

        log.debug("Add 'publisher_pre_delete' signal handler to %s", repr(model))
        models.signals.pre_delete.connect(publisher_pre_delete, model)

        # log.debug("Add 'publisher_post_save' signal handler to %s", repr(model))
        # models.signals.post_save.connect(publisher_post_save, model)


    def current(self):
        if get_draft_status():
            return self.drafts()
        return self.published()


PublisherManager = BasePublisherManager.from_queryset(PublisherQuerySet)

try:
    from parler.managers import TranslatableManager, TranslatableQuerySet
except ImportError:
    pass
else:
    class PublisherParlerQuerySet(PublisherQuerySet, TranslatableQuerySet):
        pass

    class BasePublisherParlerManager(PublisherManager, TranslatableManager):
        def get_queryset(self):
            return PublisherParlerQuerySet(self.model, using=self._db)

    PublisherParlerManager = BasePublisherParlerManager.from_queryset(PublisherParlerQuerySet)
