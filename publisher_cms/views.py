import logging
from urllib.parse import urlencode

from django.template.defaultfilters import truncatechars
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView
from django.views.generic.detail import DetailView

from cms.toolbar.items import ButtonList

from publisher.models import PublisherModelBase, PublisherStateModel
from publisher.permissions import can_publish_instance, can_publish_object
from publisher.views import PublisherViewMixin

log = logging.getLogger(__name__)


class PublisherCmsViewMixin(PublisherViewMixin):
    def get_queryset(self):
        # django_cms_tools.permissions.EditModeAndChangePermissionMixin#edit_mode_and_change_permission
        if not self.model.edit_mode_and_change_permission(self.request):
            log.info("Not in edit mode or User has no change permission: Display only 'public' items.")
            return super(PublisherCmsViewMixin, self).get_queryset()
        else:
            log.info("edit mode is on and User has change permission: List only 'drafts' items.")
            return self.model.objects.drafts()


class PublisherCmsDetailView(PublisherCmsViewMixin, DetailView):
    # key and name of the "item" toolbar
    toolbar_key = None
    toolbar_verbose_name = None

    def __init__(self, *args, **kwargs):
        """
        Overwrite this and set self.language if parler is used,
        to append "?language=<XY>" in edit links
        """
        self.language = None
        super().__init__(*args, **kwargs)

    def _add_toolbar_button(self, name, url, disabled=False):
        toolbar = self.request.toolbar
        button_list = ButtonList(side=toolbar.RIGHT)

        # TODO: Use button_list.add_modal_button() and generate the right response for page reload!
        # button_list.add_modal_button(
        button_list.add_button(
            name=name,
            url=url,
            disabled=disabled,
            extra_classes=('cms-btn-action',),
        )
        toolbar.add_item(button_list)

    def get_instance_name(self, publisher_instance):
        """
        Build text for publish buttons.
        """
        return "'%s'" % publisher_instance._meta.verbose_name

    def _append_change_link(self, publisher_instance, instance_name):
        """
        Append admin change view link to toolbar menu.
        """
        if not self.toolbar_key or not self.toolbar_verbose_name:
            log.debug("Don't append 'admin change link', because toolbar key/name not set.")
            return

        log.debug("Append change link to %r", self.toolbar_key)

        menu = self.request.toolbar.get_or_create_menu(self.toolbar_key, self.toolbar_verbose_name)
        menu.add_break()

        url = publisher_instance.admin_change() # PublisherModelBase.admin_change()
        if self.language:
            url += "?%s" % urlencode({"language": self.language})

        menu.add_modal_item(
            _('Change {name} in admin').format(name=instance_name),
            url=url
        )

    def extend_toolbar(self, publisher_instance):
        """
        Add publish links to toolbar for current instance.
        Note:
            This method will not be called automaticly!
            A good point for a call is self.get_object()
        """
        user = self.request.user
        if not PublisherStateModel.has_change_permission(user, raise_exception=False):
            log.debug("Skip extend cms toolbar: User can't change PublisherStateModel.")
            return

        if not publisher_instance.has_change_permission(user, raise_exception=False):
            log.debug("Skip extend cms toolbar: User can't change publisher instance.")
            return

        toolbar = self.request.toolbar
        if not toolbar.edit_mode:
            log.debug("Skip extend cms toolbar: We are not in edit mode.")
            return

        can_publish = can_publish_instance(user, publisher_instance, raise_exception=False)

        draft = publisher_instance.get_draft_object()
        open_requests = PublisherStateModel.objects.get_open_requests(publisher_instance = draft)
        pending_request = open_requests.count() > 0

        instance_name = self.get_instance_name(publisher_instance)

        if pending_request:
            log.debug("Current publisher instance has open publishing requests.")
            current_request = open_requests.latest()
            if not can_publish:
                self._add_toolbar_button(
                    name=_("pending {action} {state}").format(
                        action=current_request.action_name,
                        state=current_request.state_name,
                    ),
                    url="",
                    disabled=True,
                )
                # The publisher instance has pending request: The User should not be able to edit it.
                # But we need the "edit mode": The user should raise into 404
                # if current page is not published yet!
                # see also:
                #    https://github.com/wearehoods/django-ya-model-publisher/issues/9
                log.debug("Turn off edit mode, because publisher instance as pending requests")
                toolbar.edit_mode = False
                return

            log.debug("publisher instance has pending request and user can publish: Add 'reply' button")
            self._add_toolbar_button(
                name=_("Reply {action} {name} {state}").format(
                    action=current_request.action_name,
                    name=instance_name,
                    state=current_request.state_name,
                ),
                url=current_request.admin_reply_url()
            )
            return

        log.debug("Current publisher instance has no open publishing requests.")
        if publisher_instance.is_dirty:
            if not can_publish:
                log.debug("publisher instance is dirty, user can't publish: Add request publish button")
                self._add_toolbar_button(
                    name=_("Request publishing {name}").format(name=instance_name),
                    url=PublisherStateModel.objects.admin_request_publish_url(obj=publisher_instance)
                )
            else:
                log.debug("publisher instance is dirty, user can publish: Add publish button")
                self._add_toolbar_button(
                    name=_("Publish {name}").format(name=instance_name),
                    url=draft.admin_publish_url()
                )
        else:
            self._append_change_link(draft, instance_name)
            if not can_publish:
                log.debug("publisher instance is dirty, user can't publish: Add request unpublish button")
                self._add_toolbar_button(
                    name=_("Request unpublishing {name}").format(name=instance_name),
                    url=PublisherStateModel.objects.admin_request_unpublish_url(obj=publisher_instance)
                )
            else:
                log.debug("publisher instance is dirty, user can publish: Add unpublish button")
                self._add_toolbar_button(
                    name=_("Unpublish {name}").format(name=instance_name),
                    url=draft.admin_unpublish_url()
                )


class PublisherCmsListView(PublisherCmsViewMixin, ListView):
    pass
