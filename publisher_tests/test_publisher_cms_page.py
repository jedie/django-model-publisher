
import sys
from unittest import mock

import pytest

from django.core.management import call_command

from cms.models import Page

from django_tools.unittest_utils.BrowserDebug import debug_response
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer

from publisher import constants
from publisher.models import PublisherStateModel
from publisher_tests.base import CmsBaseTestCase


@pytest.mark.django_db
class CmsPagePublisherWorkflowTests(CmsBaseTestCase):
    """
    Publisher workflow for CMS pages
    """
    def setUp(self):
        super(CmsPagePublisherWorkflowTests, self).setUp()

        public_pages = Page.objects.public()
        self.assertEqual(public_pages.count(), 1)

        page = public_pages[0]
        page.refresh_from_db()

        self.page4edit = page.get_draft_object()
        self.page4edit.refresh_from_db()

        self.page4edit_url = self.page4edit.get_absolute_url(language="en")

        self.page4edit_title = self.page4edit.get_title_obj(language="en")
        self.page4edit_title.refresh_from_db()

        # self.parent_page4edit = self.page4edit.parent.get_draft_object()
        # self.parent_page4edit_url = self.parent_page4edit.get_absolute_url(language="en")

    def test_setUp(self):
        self.assertEqual(self.page4edit_url, "/en/")
        self.assertEqual(self.page4edit.publisher_is_draft, True)
        self.assertEqual(self.page4edit.is_dirty(language="en"), False)

        self.assertEqual(str(self.page4edit_title), "Test page in English (test-page-in-english, en)")

        # self.assertEqual(self.parent_page4edit_url, "/en/XXX/")
        # self.assertEqual(self.parent_page4edit.get_title(language="en"), "XXX")
        # self.assertEqual(self.parent_page4edit.publisher_is_draft, True)
        # self.assertEqual(self.parent_page4edit.is_dirty(language="en"), False)

    def test_reporter_permissions(self):
        with StdoutStderrBuffer() as buff:
            call_command("permission_info", "reporter")
        output = buff.get_output()

        output = [line.strip(" \t_") for line in output.splitlines()]
        output = "\n".join([line for line in output if line])
        # print(output)

        # 'reporter' user can create un-/publish requests:

        self.assertIn("[*] cms.change_page", output) # Can change a Django CMS page
        self.assertIn("[ ] cms.publish_page", output) # Can't publish a Django CMS page changes

        # 'reporter' user can create un-/publish requests:
        # self.assertIn("[*] publisher.add_publisherstatemodel", output)
        self.assertIn("[*] publisher.ask_publisher_request", output)
        # self.assertIn("[*] publisher.change_publisherstatemodel", output)
        # self.assertIn("[*] publisher.delete_publisherstatemodel", output)
        # self.assertIn("[ ] publisher.direct_publisher", output)
        self.assertIn("[ ] publisher.reply_publisher_request", output)

    def test_editor_permissions(self):
        with StdoutStderrBuffer() as buff:
            call_command("permission_info", "editor")
        output = buff.get_output()

        output = [line.strip(" \t_") for line in output.splitlines()]
        output = "\n".join([line for line in output if line])
        # print(output)

        # 'editor' user can accept/reject un-/publish requests:

        self.assertIn("[*] cms.change_page", output) # Can change a Django CMS page
        self.assertIn("[ ] cms.publish_page", output) # Can't publish a Django CMS page changes

        # 'editor' user can accept/reject un-/publish requests:
        # self.assertIn("[*] publisher.add_publisherstatemodel", output)
        self.assertIn("[ ] publisher.ask_publisher_request", output)
        # self.assertIn("[*] publisher.change_publisherstatemodel", output)
        # self.assertIn("[*] publisher.delete_publisherstatemodel", output)
        # self.assertIn("[ ] publisher.direct_publisher", output)
        self.assertIn("[*] publisher.reply_publisher_request", output)

    def test_reporter_edit_unchanged_page(self):
        self.login_reporter_user()

        response = self.client.get(
            "%s?edit" % self.page4edit_url,
            HTTP_ACCEPT_LANGUAGE="en"
        )
        # debug_response(response)

        # 'reporter' user can create un-/publish requests:

        self.assertResponse(response,
            must_contain=(
                "django-ya-model-publisher", "Test page in English",

                "Logout reporter",
                "Double-click to edit",

                # <a href="/en/admin/publisher/publisherstatemodel/2/23/request_unpublish/"...>Request unpublishing</a>
                "/request_unpublish/", "Request unpublishing",
            ),
            must_not_contain=(
                # <a href="/en/admin/cms/page/670/en/publish/"...>Publish page changes</a>
                "/publish/", "Publish page changes",

                # <a href="/de/admin/publisher/publisherstatemodel/2/614/request_publish/"...>Request publishing</a>
                "/request_publish/", "Request publishing",

                "Error", "Traceback",
            ),
            status_code=200,
            template_name="cms/base.html",
            html=False,
        )

    def test_editor_edit_unchanged_page(self):
        self.login_editor_user()

        response = self.client.get(
            "%s?edit" % self.page4edit_url,
            HTTP_ACCEPT_LANGUAGE="en"
        )
        # debug_response(response)

        # 'editor' user can accept/reject un-/publish requests:

        self.assertResponse(response,
            must_contain=(
                "django-ya-model-publisher", "Test page in English",

                "Logout editor",
                "Double-click to edit",
            ),
            must_not_contain=(
                # <a href="/en/admin/cms/page/670/en/publish/"...>Publish page changes</a>
                "/publish/", "Publish page changes",

                # <a href="/en/admin/publisher/publisherstatemodel/2/23/request_unpublish/"...>Request unpublishing</a>
                "/request_unpublish/", "Request unpublishing",

                # <a href="/de/admin/publisher/publisherstatemodel/2/614/request_publish/"...>Request publishing</a>
                "/request_publish/", "Request publishing",

                "Error", "Traceback",
            ),
            status_code=200,
            template_name="cms/base.html",
            html=False,
        )

    def test_reporter_edit_dirty_page(self):
        self.login_reporter_user() # can create un-/publish requests

        self.page4edit_title.title = "A new page title"
        self.page4edit_title.save()

        self.assertEqual(self.page4edit.is_dirty(language="en"), True)

        response = self.client.get(
            "%s?edit" % self.page4edit_url,
            HTTP_ACCEPT_LANGUAGE="en"
        )
        # debug_response(response)

        # 'reporter' user can create un-/publish requests:

        self.assertResponse(response,
            must_contain=(
                "A new page title",

                "Logout reporter",
                "Double-click to edit",

                # <a href="/de/admin/publisher/publisherstatemodel/2/614/request_publish/"...>Request publishing</a>
                "/request_publish/", "Request publishing",

                # <a href="/en/admin/publisher/publisherstatemodel/2/23/request_unpublish/"...>Request unpublishing</a>
                "/request_unpublish/", "Request unpublishing",
            ),
            must_not_contain=(
                # <a href="/en/admin/cms/page/670/en/publish/"...>Publish page changes</a>
                "/publish/", "Publish page changes",

                "Error", "Traceback",
            ),
            status_code=200,
            template_name="cms/base.html",
            html=False,
        )

    def test_reporter_edit_pending_page(self):
        reporter = self.login_reporter_user() # can create un-/publish requests
        self.assertTrue(reporter.has_perm("cms.change_page"))

        self.page4edit_title.title = "A new page title"
        self.page4edit_title.save()

        self.assertEqual(self.page4edit.is_dirty(language="en"), True)

        state_instance = PublisherStateModel.objects.request_publishing(
            user = reporter,
            publisher_instance = self.page4edit
        )

        response = self.client.get(
            "%s?edit" % self.page4edit_url,
            HTTP_ACCEPT_LANGUAGE="en",
        )

        self.assertRedirects(
            response,
            expected_url="%s?edit_off" % self.page4edit_url,
            fetch_redirect_response=False
        )

        # TODO: Check if user get a message

    def test_reporter_publish_request_view(self):
        reporter = self.login_reporter_user() # can create un-/publish requests
        self.assertTrue(reporter.has_perm("cms.change_page"))

        self.page4edit_title.title = "A new page title"
        self.page4edit_title.save()

        self.assertEqual(self.page4edit.is_dirty(language="en"), True)

        request_publish_url = PublisherStateModel.objects.admin_request_publish_url(self.page4edit)
        print(request_publish_url)
        self.assert_startswith(request_publish_url, "/en/admin/publisher/publisherstatemodel/")
        self.assert_endswith(request_publish_url, "/request_publish/")

        response = self.client.get(request_publish_url, HTTP_ACCEPT_LANGUAGE="en")
        # debug_response(response)

        self.assertResponse(response,
            must_contain=(
                "Publisher",
                "Publisher States",
                "Request Publishing",

                "Note:",
                "Publisher History",
                "No changes, yet.",
            ),
            must_not_contain=("Error", "Traceback"),
            status_code=200,
            template_name="publisher/publisher_requests.html",
            html=False,
        )

    def test_reporter_create_publish_request(self):

        self.assertEqual(PublisherStateModel.objects.all().count(), 0)

        reporter = self.login_reporter_user() # can create un-/publish requests
        self.assertTrue(reporter.has_perm("cms.change_page"))

        self.page4edit_title.title = "A new page title"
        self.page4edit_title.save()

        self.assertEqual(self.page4edit.is_dirty(language="en"), True)

        request_publish_url = PublisherStateModel.objects.admin_request_publish_url(self.page4edit)
        print(request_publish_url)
        self.assert_startswith(request_publish_url, "/en/admin/publisher/publisherstatemodel/")
        self.assert_endswith(request_publish_url, "/request_publish/")

        response = self.client.post(
            request_publish_url,
            data={
                "note": "Please publish this cms page changes.",
                "_ask_publish": "This value doesn't really matter.",
            },
            HTTP_ACCEPT_LANGUAGE="de"
        )
        # debug_response(response)

        self.assertRedirects(response,
            expected_url="http://testserver/en/?edit_off",
            status_code=302,
            fetch_redirect_response=False
        )

        self.assertEqual(PublisherStateModel.objects.all().count(), 1)

        state = PublisherStateModel.objects.all()[0]
        self.assertEqual(
            str(state),
            '"A new page title" publish request from: reporter (Please publish this cms page changes.) (open)'
        )
        self.assertEqual(state.publisher_instance.pk, self.page4edit.pk)

    def test_reporter_unpublish_request_view(self):
        reporter = self.login_reporter_user() # can create un-/publish requests
        self.assertTrue(reporter.has_perm("cms.change_page"))

        self.assertEqual(self.page4edit.is_dirty(language="en"), False)

        request_unpublish_url = PublisherStateModel.objects.admin_request_unpublish_url(self.page4edit)
        print(request_unpublish_url)
        self.assert_startswith(request_unpublish_url, "/en/admin/publisher/publisherstatemodel/")
        self.assert_endswith(request_unpublish_url, "/request_unpublish/")

        response = self.client.get(request_unpublish_url, HTTP_ACCEPT_LANGUAGE="en")
        # debug_response(response)

        self.assertResponse(response,
            must_contain=(
                "Publisher",
                "Publisher States",
                "Request Unpublishing",

                "Note:",
                "Publisher History",
                "No changes, yet.",
            ),
            must_not_contain=("Error", "Traceback"),
            status_code=200,
            template_name="publisher/publisher_requests.html",
            html=False,
        )

    def test_reporter_create_unpublish_request(self):

        self.assertEqual(PublisherStateModel.objects.all().count(), 0)

        reporter = self.login_reporter_user() # can create un-/publish requests
        self.assertTrue(reporter.has_perm("cms.change_page"))

        self.assertEqual(self.page4edit.is_dirty(language="en"), False)

        request_unpublish_url = PublisherStateModel.objects.admin_request_unpublish_url(self.page4edit)
        print(request_unpublish_url)
        self.assert_startswith(request_unpublish_url, "/en/admin/publisher/publisherstatemodel/")
        self.assert_endswith(request_unpublish_url, "/request_unpublish/")

        response = self.client.post(
            request_unpublish_url,
            data={
                "note": "Please unpublish this cms page.",
                "_ask_publish": "This value doesn't really matter.",
            },
            HTTP_ACCEPT_LANGUAGE="de"
        )
        # debug_response(response)

        self.assertRedirects(response,
            expected_url="http://testserver/en/?edit_off",
            status_code=302,
            fetch_redirect_response=False
        )

        self.assertEqual(PublisherStateModel.objects.all().count(), 1)

        state = PublisherStateModel.objects.all()[0]
        self.assertEqual(
            str(state),
            '"Test page in English" unpublish request from: reporter (Please unpublish this cms page.) (open)'
        )
        self.assertEqual(state.publisher_instance.pk, self.page4edit.pk)


    #-------------------------------------------------------------------------


    def test_editor_reply_publish_request_view(self):
        self.page4edit_title.title = "A new page title"
        self.page4edit_title.save()

        self.assertEqual(self.page4edit.is_dirty(language="en"), True)

        reporter_user = self.UserModel.objects.get(username="reporter")
        state_instance = PublisherStateModel.objects.request_publishing(
            user = reporter_user,
            publisher_instance = self.page4edit
        )

        reply_url = state_instance.admin_reply_url()
        print(reply_url)
        self.assert_startswith(reply_url, "/en/admin/publisher/publisherstatemodel/")
        self.assert_endswith(reply_url, "/reply_request/")

        self.login_editor_user() # can accept/reject un-/publish requests

        response = self.client.get(reply_url, HTTP_ACCEPT_LANGUAGE="en")
        # debug_response(response)

        self.assertResponse(response,
            must_contain=(
                "Publisher",
                "Publisher States",
                "Accept/Reject Publish Request",
                "Note:",
                "&quot;A new page title&quot; publish request from: reporter (open)",
                "Publisher History",
            ),
            must_not_contain=(
                "No changes, yet.",
                "Error", "Traceback"
            ),
            status_code=200,
            template_name="publisher/publisher_requests.html",
            html=False,
        )

    def test_editor_accept_publish_request(self):
        self.page4edit_title.title = "A new page title"
        self.page4edit_title.save()

        self.assertEqual(self.page4edit.is_dirty(language="en"), True)

        reporter_user = self.UserModel.objects.get(username="reporter")
        state_instance = PublisherStateModel.objects.request_publishing(
            user = reporter_user,
            publisher_instance = self.page4edit
        )

        reply_url = state_instance.admin_reply_url()
        print(reply_url)
        self.assert_startswith(reply_url, "/en/admin/publisher/publisherstatemodel/")
        self.assert_endswith(reply_url, "/reply_request/")

        self.login_editor_user()

        def raise_error(*args, **kwargs):
            tb = sys.exc_info()[2]
            raise AssertionError().with_traceback(tb)

        # django/conf/urls/__init__.py:13 - handler400
        with mock.patch('django.views.defaults.bad_request', new=raise_error):
            response = self.client.post(
                reply_url,
                data={
                    "note": "OK, I publish this cms page, now.",
                    constants.POST_REPLY_ACCEPT_KEY: "This value doesn't really matter.",
                },
                HTTP_ACCEPT_LANGUAGE="de"
            )
            # debug_response(response)

        self.assertRedirects(response,
            expected_url="http://testserver/en/",
            status_code=302,
            fetch_redirect_response=False
        )

        self.assertEqual(PublisherStateModel.objects.all().count(), 1)

        state = PublisherStateModel.objects.all()[0]
        self.assertEqual(
            str(state),
            '"A new page title" publish accepted from: editor (OK, I publish this cms page, now.)'
        )
        self.assertEqual(state.publisher_instance.pk, self.page4edit.pk)

        self.page4edit = Page.objects.get(pk=self.page4edit.pk)
        self.assertEqual(self.page4edit.is_dirty(language="en"), False)

    def test_editor_reject_publish_request(self):
        self.page4edit_title.title = "A new page title"
        self.page4edit_title.save()

        self.assertEqual(self.page4edit.is_dirty(language="en"), True)

        reporter_user = self.UserModel.objects.get(username="reporter")
        state_instance = PublisherStateModel.objects.request_publishing(
            user = reporter_user,
            publisher_instance = self.page4edit
        )

        reply_url = state_instance.admin_reply_url()
        print(reply_url)
        self.assert_startswith(reply_url, "/en/admin/publisher/publisherstatemodel/")
        self.assert_endswith(reply_url, "/reply_request/")

        self.login_editor_user() # can accept/reject un-/publish requests

        def raise_error(*args, **kwargs):
            tb = sys.exc_info()[2]
            raise AssertionError().with_traceback(tb)

        # django/conf/urls/__init__.py:13 - handler400
        with mock.patch('django.views.defaults.bad_request', new=raise_error):
            response = self.client.post(
                reply_url,
                data={
                    "note": "No, I reject this request.",
                    constants.POST_REPLY_REJECT_KEY: "This value doesn't really matter.",
                },
                HTTP_ACCEPT_LANGUAGE="de"
            )
            # debug_response(response)

        self.assertRedirects(response,
            expected_url="http://testserver/en/",
            status_code=302,
            fetch_redirect_response=False
        )

        self.assertEqual(PublisherStateModel.objects.all().count(), 1)

        state = PublisherStateModel.objects.all()[0]
        self.assertEqual(
            str(state),
            '"A new page title" publish rejected from: editor (No, I reject this request.)'
        )
        self.assertEqual(state.publisher_instance.pk, self.page4edit.pk)

        self.page4edit = Page.objects.get(pk=self.page4edit.pk)
        self.assertEqual(self.page4edit.is_dirty(language="en"), True)