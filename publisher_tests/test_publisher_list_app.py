
"""
    created 2017-2018  by Jens Diemer <ya-publisher@jensdiemer.de>
"""

import sys
from unittest import mock

import django
from django.contrib.contenttypes.models import ContentType
from django.test.utils import override_settings

from cms.models import Page

from publisher.models import PublisherStateModel
from publisher_test_project.publisher_list_app.models import PublisherItem
from publisher_tests.base import ClientBaseTestCase


@override_settings(LOGGING={})
class PublisherItemAppTestCase(ClientBaseTestCase):
    """
    PublisherItem test instances made with:

    publisher_test_project.publisher_list_app.fixtures.list_item_fixtures()

    'reporter' user has not 'can_publish' -> can only create un-/publish requests
    'editor' user has 'can_publish' -> can publish and accept/reject un-/publish requests
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # $ ./publisher_test_project/manage.py cms_page_info application_urls application_namespace navigation_extenders

        list_page = Page.objects.public().get(application_namespace="PublisherItem")
        cls.list_page_url = list_page.get_absolute_url(language="en")

        def get_item(text):
            qs = PublisherItem.objects.translated("en", text=text).language("en")
            item = qs.get(publisher_is_draft=True) # used the draft version
            url = item.get_absolute_url(language="en")
            return item, url

        cls.not_published_item, cls.not_published_item_url = get_item("Not published Item")
        cls.published_item, cls.published_item_url = get_item("Published Item")
        cls.hidden_by_start_date_item, cls.hidden_by_start_date_item_url = get_item("hidden by start date")
        cls.hidden_by_end_date_item, cls.hidden_by_end_date_item_url = get_item("hidden by end date")
        cls.dirty_item, cls.dirty_item_url = get_item("This is dirty!")

        cls.pending_publish_item, cls.pending_publish_item_url = get_item("pending publish request")
        cls.pending_unpublish_item, cls.pending_unpublish_item_url = get_item("pending unpublish request")

        content_type_id = ContentType.objects.get_for_model(PublisherItem).pk
        cls.dirty_item_request_publish_url = "/en/admin/publisher/publisherstatemodel/%i/%i/request_publish/" % (
            content_type_id, cls.dirty_item.pk
        )
        cls.published_item_request_unpublish_url = "/en/admin/publisher/publisherstatemodel/%i/%i/request_unpublish/" % (
            content_type_id, cls.published_item.pk
        )

    def get_admin_change_url(self, obj):
        assert obj.publisher_is_draft == True, "%s not draft!" % obj
        url = super(PublisherItemAppTestCase, self).get_admin_change_url(obj)
        url += "?language=en"
        return url

    def test_setUp(self):
        self.assertEqual(self.list_page_url, "/en/publisheritems/")

        self.assertEqual(self.not_published_item.slug, "not-published-item")
        self.assertEqual(self.not_published_item.is_published, False)
        self.assertEqual(self.not_published_item.get_public_object(), None) # Not published
        self.assertEqual(self.not_published_item.hidden_by_end_date, False)
        self.assertEqual(self.not_published_item.hidden_by_start_date, False)
        self.assertEqual(self.not_published_item.is_visible, False)
        self.assertEqual(self.not_published_item.is_dirty, True)
        self.assertEqual(self.not_published_item_url, "/en/publisheritems/not-published-item/")

        self.assertEqual(self.published_item.slug, "published-item")
        self.assertEqual(self.published_item.is_published, False) # It's the draft, not the published instance
        self.assertEqual(self.published_item.get_public_object().is_published, True)
        self.assertEqual(self.published_item.hidden_by_end_date, False)
        self.assertEqual(self.published_item.hidden_by_start_date, False)
        self.assertEqual(self.published_item.is_visible, True)
        self.assertEqual(self.published_item.is_dirty, False)
        self.assertEqual(self.published_item_url, "/en/publisheritems/published-item/")

        self.assertEqual(self.hidden_by_start_date_item.slug, "hidden-by-start-date")
        self.assertEqual(self.hidden_by_start_date_item.is_published, False)
        self.assertEqual(self.hidden_by_start_date_item.get_public_object().is_published, True)
        self.assertEqual(self.hidden_by_start_date_item.hidden_by_end_date, False)
        self.assertEqual(self.hidden_by_start_date_item.hidden_by_start_date, True)
        self.assertEqual(self.hidden_by_start_date_item.is_visible, False)
        self.assertEqual(self.hidden_by_start_date_item.is_dirty, False)
        self.assertEqual(self.hidden_by_start_date_item_url, "/en/publisheritems/hidden-by-start-date/")

        self.assertEqual(self.hidden_by_end_date_item.slug, "hidden-by-end-date")
        self.assertEqual(self.hidden_by_end_date_item.is_published, False)
        self.assertEqual(self.hidden_by_end_date_item.get_public_object().is_published, True)
        self.assertEqual(self.hidden_by_end_date_item.hidden_by_end_date, True)
        self.assertEqual(self.hidden_by_end_date_item.hidden_by_start_date, False)
        self.assertEqual(self.hidden_by_end_date_item.is_visible, False)
        self.assertEqual(self.hidden_by_end_date_item.is_dirty, False)
        self.assertEqual(self.hidden_by_end_date_item_url, "/en/publisheritems/hidden-by-end-date/")

        self.assertEqual(self.dirty_item.slug, "dirty")
        self.assertEqual(self.dirty_item.is_published, False)
        self.assertEqual(self.dirty_item.get_public_object().is_published, True)
        self.assertEqual(self.dirty_item.hidden_by_end_date, False)
        self.assertEqual(self.dirty_item.hidden_by_start_date, False)
        self.assertEqual(self.dirty_item.is_visible, True)
        self.assertEqual(self.dirty_item.is_dirty, True)
        self.assertEqual(self.dirty_item_url, "/en/publisheritems/dirty/")

        self.assertEqual(self.pending_publish_item.slug, "pending-publish-request")
        self.assertEqual(self.pending_publish_item.is_published, False)
        self.assertEqual(self.pending_publish_item.get_public_object(), None) # Not published
        self.assertEqual(self.pending_publish_item.hidden_by_end_date, False)
        self.assertEqual(self.pending_publish_item.hidden_by_start_date, False)
        self.assertEqual(self.pending_publish_item.is_visible, False)
        self.assertEqual(self.pending_publish_item.is_dirty, True)
        self.assertEqual(self.pending_publish_item_url, "/en/publisheritems/pending-publish-request/")

        self.assertEqual(self.pending_unpublish_item.slug, "pending-unpublish-request")
        self.assertEqual(self.pending_unpublish_item.is_published, False) # It's the draft, not the published instance
        self.assertEqual(self.pending_unpublish_item.get_public_object().is_published, True)
        self.assertEqual(self.pending_unpublish_item.hidden_by_end_date, False)
        self.assertEqual(self.pending_unpublish_item.hidden_by_start_date, False)
        self.assertEqual(self.pending_unpublish_item.is_visible, True)
        self.assertEqual(self.pending_unpublish_item.is_dirty, False)
        self.assertEqual(self.pending_unpublish_item_url, "/en/publisheritems/pending-unpublish-request/")

        url = self.get_admin_change_url(obj=self.published_item)
        if django.VERSION < (1, 11):
            self.assertEqual(url,
                "/en/admin/publisher_list_app/publisheritem/%i/?language=en" % self.published_item.pk
            )
        else:
            self.assertEqual(url,
                "/en/admin/publisher_list_app/publisheritem/%i/change/?language=en" % self.published_item.pk
            )

    #-------------------------------------------------------------------------

    def test_anonymous_list_item_page(self):
        response = self.client.get(self.list_page_url, HTTP_ACCEPT_LANGUAGE="en")
        self.assertResponse(response,
            must_contain=(
                "Publisher List App - list view",

                "/en/publisheritems/published-item/", "Published Item",
                "/en/publisheritems/dirty/", "dirty",
            ),
            must_not_contain=(
                "Error", "Traceback",
            ),
            status_code=200,
            template_name="list_app/list.html",
            html=False,
        )

    def test_anonymous_list_item_detail_page(self):
        response = self.client.get(self.published_item_url, HTTP_ACCEPT_LANGUAGE="en")
        self.assertResponse(response,
            must_contain=(
                "Publisher List App - detail view",

                "Published Item",
            ),
            must_not_contain=(
                "Error", "Traceback",
            ),
            status_code=200,
            template_name="list_app/detail.html",
            html=False,
        )

    #-------------------------------------------------------------------------

    def test_anonymous_hidden(self):
        response = self.client.get(self.not_published_item_url, HTTP_ACCEPT_LANGUAGE="en")
        # self.debug_response(response)
        self.assertResponse(response,
            must_contain=("Not Found",),
            must_not_contain=None,
            status_code=404,
            template_name=None,
            html=False,
            browser_traceback=True
        )

    #-------------------------------------------------------------------------

    def test_editor_edit_list_item_admin_view(self):
        self.login_editor_user()

        response = self.client.get(
            self.get_admin_change_url(obj=self.dirty_item),
            HTTP_ACCEPT_LANGUAGE="en"
        )
        # self.debug_response(response)

        # 'editor' user has 'can_publish' -> can publish and accept/reject un-/publish requests:

        self.assertResponse(response,
            must_contain=(
                "user 'editor'",
                "Change publisher item (English)",

                "Text:", "This is dirty!",
                "Slug:", "dirty",

                # publisher submit buttons:
                "_save", "Save draft",
                "_save_published", "Save and Publish",

                "Publisher History", "No changes, yet.",
            ),
            must_not_contain=(
                "_ask_publish", "Request Publishing",
                "_ask_unpublish", "Request Unpublishing",

                "send publish request",
                "Note:", # publisher note textarea

                "Error", "Traceback"
            ),
            status_code=200,
            template_name="publisher/parler/change_form.html",
            html=False,
        )

    def test_reporter_edit_list_item_admin_view(self):
        self.login_reporter_user()

        response = self.client.get(
            self.get_admin_change_url(obj=self.dirty_item),
            HTTP_ACCEPT_LANGUAGE="en"
        )
        # self.debug_response(response)

        # 'reporter' user has not 'can_publish' -> can only create un-/publish requests:

        self.assertResponse(response,
            must_contain=(
                "user 'reporter'",
                "Change publisher item (English)",

                "Text:", "This is dirty!",
                "Slug:", "dirty",

                # publisher submit buttons:

                "_ask_publish", "Request Publishing",
                "_ask_unpublish", "Request Unpublishing",

                "send publish request",
                "Note:", # publisher note textarea

                "Publisher History", "No changes, yet.",
            ),
            must_not_contain=(
                "_save", "Save draft",
                "_save_published", "Save and Publish",

                "Error", "Traceback"
            ),
            status_code=200,
            template_name="publisher/parler/change_form.html",
            html=False,
        )
    def test_reporter_changelist_admin_view(self):
        self.login_reporter_user()

        response = self.client.get(
            "/en/admin/publisher_list_app/publisheritem/",
            HTTP_ACCEPT_LANGUAGE="en"
        )
        # self.debug_response(response)

        # 'reporter' user has not 'can_publish' -> can only create un-/publish requests:

        self.assertResponse(response,
            must_contain=(
                "Django administration",

                "user 'reporter'",

                # FIXME: Check correct assignment:

                "This is dirty!", "Changes not yet published. Older version is online.",
                "hidden by end date", "Published, but hidden by end date.",
                "hidden by start date", "Published, but hidden by start date.",
                "Published Item", "Is public.",
                "Not published Item", "Not published, yet",
                "pending unpublish request", "is public",
                "pending publish request", "not public",

                "7 publisher items",
            ),
            must_not_contain=(
                "Error", "Traceback"
            ),
            status_code=200,
            template_name="admin/change_list.html",
            html=False,
        )

    def test_editor_list_page_view_no_edit(self):
        self.login_editor_user()

        response = self.client.get(
            self.list_page_url,
            HTTP_ACCEPT_LANGUAGE="en"
        )
        # self.debug_response(response)

        # 'editor' user has 'can_publish' -> can publish and accept/reject un-/publish requests:

        self.assertResponse(response,
            must_contain=(
                "user 'editor'",

                # Toolbar links:
                "open requests",
                "unpublish: pending unpublish request",
                "publish: pending publish request",

                # App content:
                "Publisher List App - list view",

                "/en/publisheritems/published-item/", "Published Item",
                "/en/publisheritems/dirty/", "dirty",
                "/en/publisheritems/pending-unpublish-request/", "pending unpublish request",
            ),
            must_not_contain=(
                "/en/publisheritems/not-published-item", "Not published Item",
                "/en/publisheritems/hidden-by-start-date", "hidden by start date",
                "/en/publisheritems/hidden-by-end-date", "hidden by end date",

                "Error", "Traceback",
            ),
            status_code=200,
            template_name="list_app/list.html",
            html=False,
        )

    def test_editor_list_page_view_edit(self):
        self.login_editor_user()

        response = self.client.get(
            self.list_page_url + "?edit",
            HTTP_ACCEPT_LANGUAGE="en"
        )
        # self.debug_response(response)

        # 'editor' user has 'can_publish' -> can publish and accept/reject un-/publish requests:

        self.assertResponse(response,
            must_contain=(
                "user 'editor'",

                # Toolbar links:
                "open requests",
                "unpublish: pending unpublish request",
                "publish: pending publish request",

                # App content:
                "Publisher List App - list view",

                "/en/publisheritems/not-published-item", "Not published Item",
                "/en/publisheritems/published-item", "Published Item",
                "/en/publisheritems/hidden-by-start-date", "hidden by start date",
                "/en/publisheritems/hidden-by-end-date", "hidden by end date",
                "/en/publisheritems/dirty", "This is dirty!",
                "/en/publisheritems/pending-publish-request/", "pending publish request",
                "/en/publisheritems/pending-unpublish-request/", "pending unpublish request",
            ),
            must_not_contain=(
                "Error", "Traceback",
            ),
            status_code=200,
            messages=[],
            template_name="list_app/list.html",
            html=False,
        )

    def test_toolbar_editor_direct_publish(self):
        self.login_editor_user() # 'editor' user has 'can_publish' -> can publish and accept/reject un-/publish requests

        response = self.client.get(
            "%s?edit" % self.dirty_item_url,
            HTTP_ACCEPT_LANGUAGE="en"
        )
        self.assertResponse(response,
            must_contain=(
                "user 'editor'",
                "Publisher List App - detail view",
                "/en/admin/publisher_list_app/publisheritem/%i/publish/" % self.dirty_item.get_draft_object().pk,
            ),
            must_not_contain=(
                "Error", "Traceback",
            ),
            status_code=200,
            messages=[],
            template_name="list_app/detail.html",
            html=False,
        )

    def test_toolbar_editor_direct_unpublish(self):
        self.login_editor_user() # 'editor' user has 'can_publish' -> can publish and accept/reject un-/publish requests

        response = self.client.get(
            "%s?edit" % self.published_item_url,
            HTTP_ACCEPT_LANGUAGE="en"
        )
        self.assertResponse(response,
            must_contain=(
                "user 'editor'",
                "Publisher List App - detail view",
                "/en/admin/publisher_list_app/publisheritem/%i/unpublish/" % self.published_item.get_draft_object().pk,
            ),
            must_not_contain=(
                "Error", "Traceback",
            ),
            status_code=200,
            messages=[],
            template_name="list_app/detail.html",
            html=False,
        )

    def test_toolbar_reporter_request_publish(self):
        self.login_reporter_user() # 'reporter' user has not 'can_publish' -> can only create un-/publish requests

        response = self.client.get(
            "%s?edit" % self.dirty_item_url,
            HTTP_ACCEPT_LANGUAGE="en"
        )
        self.assertResponse(response,
            must_contain=(
                "user 'reporter'",
                "Publisher List App - detail view",
                "<p>This is dirty!</p>", # the self.dirty_item content
                "Request publishing &#39;publisher item&#39;", # Toolbar link Text
                self.dirty_item_request_publish_url, # Toolbar link url
            ),
            must_not_contain=(
                "Error", "Traceback",
            ),
            status_code=200,
            messages=[],
            template_name="list_app/detail.html",
            html=False,
        )

    def test_toolbar_reporter_request_unpublish(self):
        self.login_reporter_user() # 'reporter' user has not 'can_publish' -> can only create un-/publish requests

        response = self.client.get(
            "%s?edit" % self.published_item_url,
            HTTP_ACCEPT_LANGUAGE="en"
        )
        self.assertResponse(response,
            must_contain=(
                "user 'reporter'",
                "Publisher List App - detail view",
                "<p>Published Item</p>", # the self.published_item content
                "Request unpublishing &#39;publisher item&#39;", # Toolbar link Text
                self.published_item_request_unpublish_url, # Toolbar link url
            ),
            must_not_contain=(
                "Error", "Traceback",
            ),
            status_code=200,
            messages=[],
            template_name="list_app/detail.html",
            html=False,
        )

    def test_toolbar_editor_pending_publish(self):
        self.login_editor_user() # 'editor' user has 'can_publish' -> can publish and accept/reject un-/publish requests

        current_request = PublisherStateModel.objects.get_current_request(self.pending_publish_item)

        response = self.client.get(
            "%s?edit" % self.pending_publish_item_url,
            HTTP_ACCEPT_LANGUAGE="en"
        )
        self.assertResponse(response,
            must_contain=(
                "user 'editor'",
                "Publisher List App - detail view",

                # item content:
                "<p>pending publish request</p>",

                # toolbar link:
                "/en/admin/publisher/publisherstatemodel/%i/reply_request/" % current_request.pk,
                "Reply publish &#39;publisher item&#39; request",
            ),
            must_not_contain=(
                "Error", "Traceback",
            ),
            status_code=200,
            messages=[],
            template_name="list_app/detail.html",
            html=False,
        )

    def test_toolbar_editor_pending_unpublish(self):
        self.login_editor_user() # 'editor' user has 'can_publish' -> can publish and accept/reject un-/publish requests

        current_request = PublisherStateModel.objects.get_current_request(self.pending_unpublish_item)

        response = self.client.get(
            "%s?edit" % self.pending_unpublish_item_url,
            HTTP_ACCEPT_LANGUAGE="en"
        )
        self.assertResponse(response,
            must_contain=(
                "user 'editor'",
                "Publisher List App - detail view",

                # item content:
                "<p>pending unpublish request</p>",

                # toolbar link:
                "/en/admin/publisher/publisherstatemodel/%i/reply_request/" % current_request.pk,
                "Reply unpublish &#39;publisher item&#39; request",
            ),
            must_not_contain=(
                "Error", "Traceback",
            ),
            status_code=200,
            messages=[],
            template_name="list_app/detail.html",
            html=False,
        )


    def test_toolbar_reporter_pending_publish(self):
        self.login_reporter_user() # 'reporter' user has not 'can_publish' -> can only create un-/publish requests

        response = self.client.get(
            "%s?edit" % self.pending_publish_item_url,
            HTTP_ACCEPT_LANGUAGE="en"
        )
        self.assertResponse(response,
            must_contain=(
                # item content:
                "<p>pending publish request</p>",

                # Toolbar "link":
                '<a href="" class="cms-btn cms-btn-disabled cms-btn-action">pending publish request</a>'
            ),
            must_not_contain=(
                "Error", "Traceback",
            ),
            status_code=200,
            messages=[],
            template_name="list_app/detail.html",
            html=True,
        )

    def test_toolbar_reporter_pending_unpublish(self):
        self.login_reporter_user() # 'reporter' user has not 'can_publish' -> can only create un-/publish requests

        response = self.client.get(
            "%s?edit" % self.pending_unpublish_item_url,
            HTTP_ACCEPT_LANGUAGE="en"
        )
        self.assertResponse(response,
            must_contain=(
                # item content:
                "<p>pending unpublish request</p>",

                # Toolbar "link":
                '<a href="" class="cms-btn cms-btn-disabled cms-btn-action">pending unpublish request</a>'
            ),
            must_not_contain=(
                "Error", "Traceback",
            ),
            status_code=200,
            messages=[],
            template_name="list_app/detail.html",
            html=True,
        )
