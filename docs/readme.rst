====================================
Django (yet another) Model Publisher
====================================

Publisher workflow for django models and Django CMS pages.

This is a fork of `andersinno/django-model-publisher-ai <https://github.com/andersinno/django-model-publisher-ai>`_ which is a fork of the origin `jp74/django-model-publisher <https://github.com/jp74/django-model-publisher>`_.

+-----------------------------------+--------------------------------------------------------+
| |Build Status on travis-ci.org|   | `travis-ci.org/wearehoods/django-ya-model-publisher`_  |
+-----------------------------------+--------------------------------------------------------+
| |Coverage Status on codecov.io|   | `codecov.io/gh/wearehoods/django-ya-model-publisher`_  |
+-----------------------------------+--------------------------------------------------------+
| |Coverage Status on coveralls.io| | `coveralls.io/r/wearehoods/django-ya-model-publisher`_ |
+-----------------------------------+--------------------------------------------------------+

.. |Build Status on travis-ci.org| image:: https://travis-ci.org/wearehoods/django-ya-model-publisher.svg
.. _travis-ci.org/wearehoods/django-ya-model-publisher: https://travis-ci.org/wearehoods/django-ya-model-publisher/
.. |Coverage Status on codecov.io| image:: https://codecov.io/gh/wearehoods/django-ya-model-publisher/branch/develop/graph/badge.svg
.. _codecov.io/gh/wearehoods/django-ya-model-publisher: https://codecov.io/gh/wearehoods/django-ya-model-publisher
.. |Coverage Status on coveralls.io| image:: https://coveralls.io/repos/wearehoods/django-ya-model-publisher/badge.svg
.. _coveralls.io/r/wearehoods/django-ya-model-publisher: https://coveralls.io/r/wearehoods/django-ya-model-publisher

--------
Features
--------

* Django CMS page support.

* Add request/reject buttons in Django CMS toolbar.

* Django CMS placeholders support.

* Hvad/Parler support.

* Restrict user access to publish functions with user permissions.

---------
base info
---------

We have these three user types:

* A user with only a few rights (we call it **'reporter'**)

* A user with more rights (We call it **'editor'**)

* The superuser with all rights

The user case is following:

* **'reporter'**:

    * can only change draft content

    * can't change public content

    * can't delete publisher model entries or CMS pages.

    * can send a *(un-)publish request* to the 'editor' with a text node.

* **'editor'**:

    * can response open publishing request from 'reporter'.

    * can change drafts and public content, but only if there is no pending request.

    * can delete publisher model entries or CMS pages.

    * can't delete/manipulate publisher state model entries.

-----------
permissions
-----------

Permissions for **'reporter'** who can only create *(un-)publish requests*:

::

    ...
    [ ] cms.publish_page
    ...
    [*] cms.add_page
    [*] cms.change_page
    [ ] cms.delete_page
    ...
    [ ] publisher.add_publisherstatemodel
    [*] publisher.change_publisherstatemodel
    [ ] publisher.delete_publisherstatemodel
    ...
    [ ] <app_name>.can_publish_<model_name>
    ...
    [*] <app_name>.add_<model_name>
    [*] <app_name>.change_<model_name>
    [ ] <app_name>.delete_<model_name>
    ...

Permissions for **'editor'** who can *accept/reject (un-)publish requests*:

::

    ...
    [*] cms.publish_page
    ...
    [*] cms.add_page
    [*] cms.change_page
    [*] cms.delete_page
    ...
    [ ] publisher.add_publisherstatemodel
    [*] publisher.change_publisherstatemodel
    [ ] publisher.delete_publisherstatemodel
    ...
    [*] <app_name>.can_publish_<model_name>
    ...
    [*] <app_name>.add_<model_name>
    [*] <app_name>.change_<model_name>
    [*] <app_name>.delete_<model_name>
    ...

**Important**: To prevent a privilege escalation, both users must **not** have access to these models:

* django.contrib.auth.models.Permission

* django.contrib.auth.models.Group

* cms.models.PagePermission

-----------
Test users:
-----------

See user permission tests in:

* `publisher_tests.test_basics.PermissionTestCase <https://github.com/wearehoods/django-ya-model-publisher/blob/master/publisher_tests/test_basics.py>`_

------------------------------
Primary key type compatibility
------------------------------

The ``publisher.models.PublisherStateModel`` used a ``PositiveIntegerField`` for the ``GenericForeignKey`` so it can only be used for models with a integer primary keys!
See also: `https://docs.djangoproject.com/en/1.11/ref/contrib/contenttypes/#django.contrib.contenttypes.fields.GenericForeignKey <https://docs.djangoproject.com/en/1.11/ref/contrib/contenttypes/#django.contrib.contenttypes.fields.GenericForeignKey>`_

--------------------
Django compatibility
--------------------

+---------------------------+------------+----------------------+--------------------+
| django-ya-model-publisher | django cms | django version       | python             |
+===========================+============+======================+====================+
| >=v0.6.x                  | 3.4.x      | 1.11                 | 3.5, 3.6           |
+---------------------------+------------+----------------------+--------------------+
| >=v0.5.x                  | 3.4.x      | 1.8, 1.9, 1.10, 1.11 | 3.5, 3.6           |
+---------------------------+------------+----------------------+--------------------+
| v0.4.x                    | 3.4.x      | 1.8, 1.9, 1.10, 1.11 | 2.7, 3.4, 3.5, 3.6 |
+---------------------------+------------+----------------------+--------------------+

Note: See travis/tox config files for current test matrix

Currently Django CMS v3.5 is not supported, yet.
It's on the TODO, see: `issues #10 <https://github.com/wearehoods/django-ya-model-publisher/issues/10>`_

---------
run tests
---------

run tests via *py.test* with current python/environment:

::

    $ make test
    or
    $ ./setup.py test
    or
    $ python tests/manage.py test myapp

run test via *tox* e.g.:

::

    $ make tox
    or
    $ ./setup.py tox
    or
    $ tox

run test project
================

You can run the test environment by:

::

    $ ./run_test_project_dev_server.sh

or:

::

    $ ./publisher_test_project/manage.py run_test_project_dev_server

The following steps will be executed:

* Create django users if not exists:

    * A django **'superuser'**

    * The user **editor**: He can accept/reject un-/publish requests

    * The user **reporter**: He can create un-/publish requests

    * note: Both users will used the same password as the 'superuser' !

* run migration

* insert test fixtures (Create Django CMS pages)

* collect static files

* run the django development server on localhost

You can pass arguments to the helper script, e.g.:

::

    $ ./run_test_project_dev_server.sh --help
    ...
    usage: manage.py run_test_project_dev_server [-h] [--version] [-v {0,1,2,3}]
                                                 [--settings SETTINGS]
                                                 [--pythonpath PYTHONPATH]
                                                 [--traceback] [--no-color]
                                                 [--ipv6] [--nothreading]
                                                 [--noreload] [--nostatic]
                                                 [--insecure]
                                                 [addrport]
    ...

To 'reset' the test fixtures, run this:

::

    $ ./publisher_test_project/manage.py create_test_data --fresh

For a complete fresh database, just remove the sqlite file, e.g.:

::

    $ rm publisher_test_project/publisher_test_database.sqlite3

------------------------------
Backwards-incompatible changes
------------------------------

v0.7.0
======

``PublisherCmsViewMixin, PublisherCmsDetailView, PublisherCmsListView``

moved from:

``publisher.views``

to:

``publisher_cms.views``

v0.6.0
======

The permission names changed! Please update your django user permissions, too.

These permissions are removed:

* direct_publisher

* ask_publisher_request

* reply_publisher_request

Please read the information above.

-------
history
-------

* *dev* `compare v0.7.0...master <https://github.com/wearehoods/django-ya-model-publisher/compare/v0.7.0...master>`_

* v0.7.0 - 22.02.2018 - `compare v0.6.9...v0.7.0 <https://github.com/wearehoods/django-ya-model-publisher/compare/v0.6.9...v0.7.0>`_ 

    * Backwards-incompatible changes (see above)

    * Remove support for Django 1.8

    * NEW: Add publish links to Django CMS toolbar in ``PublisherCmsDetailView``

    * Change ``PublisherPageToolbar`` link text and add "page" to them (to differentiate them better from ``PublisherCmsDetailView`` links)

* v0.6.9 - 01.02.2018 - `compare v0.6.8...v0.6.9 <https://github.com/wearehoods/django-ya-model-publisher/compare/v0.6.8...v0.6.9>`_ 

    * Bugfix ``AttributeError: 'PublisherPageToolbar' object has no attribute 'current_request'`` if superuser edit a cms page

* v0.6.8 - 01.02.2018 - `compare v0.6.7...v0.6.8 <https://github.com/wearehoods/django-ya-model-publisher/compare/v0.6.7...v0.6.8>`_ 

    * Fix `#9 Redirect after "request publishing" <https://github.com/wearehoods/django-ya-model-publisher/issues/9>`_

    * Add reply/history Links in Django CMS Toolbar (specially for page with pending requests)

* v0.6.7 - 31.01.2018 - `compare v0.6.6...v0.6.7 <https://github.com/wearehoods/django-ya-model-publisher/compare/v0.6.6...v0.6.7>`_ 

    * NEW: 'History' view in admin (e.g.: see status/history of closed request and status for users that can only create requests)

    * No 404 when "reply" closed requests or deleted instance.

* v0.6.6 - 30.01.2018 - `compare v0.6.5...v0.6.6 <https://github.com/wearehoods/django-ya-model-publisher/compare/v0.6.5...v0.6.6>`_ 

    * Bugfix: redirect after "Request publishing" can result in a 404, see: `issues #9 <https://github.com/wearehoods/django-ya-model-publisher/issues/9>`_

* v0.6.5 - 30.01.2018 - `compare v0.6.4...v0.6.5 <https://github.com/wearehoods/django-ya-model-publisher/compare/v0.6.4...v0.6.5>`_ 

    * Bugfix: Missing "Request publishing" toobar link on new created pages

    * Add username list on test pages

* v0.6.4 - 29.01.2018 - `compare v0.6.3...v0.6.4 <https://github.com/wearehoods/django-ya-model-publisher/compare/v0.6.3...v0.6.4>`_ 

    * Hide PublisherStateModel admin actions for all non-superusers

* v0.6.3 - 26.01.2018 - `compare v0.6.2...v0.6.3 <https://github.com/wearehoods/django-ya-model-publisher/compare/v0.6.2...v0.6.3>`_ 

    * Security Fix: User without 'can_publish' permission can accept/reject requests.

    * Hide 'change' PublisherStateModel admin view for all non-superusers

    * Disable 'add' PublisherStateModel admin view for all users

* v0.6.2 - 02.01.2018 - `compare v0.6.1...v0.6.2 <https://github.com/wearehoods/django-ya-model-publisher/compare/v0.6.1...v0.6.2>`_ 

    * Handle publishes states with deletes instance: Add a admin view to close the request.

    * Bugfix: deny editing pending request objects

    * Create messages after (un-)/publish request created.

* v0.6.1 - 28.12.2017 - `compare v0.6.0...v0.6.1 <https://github.com/wearehoods/django-ya-model-publisher/compare/v0.6.0...v0.6.1>`_ 

    * remove own "unique_together": Add ``"publisher_is_draft"`` to your own "unique_together" tuple

    * remove out dated manage command "update_permissions" (can be found in `django-tools <https://github.com/jedie/django-tools>`_)

* v0.6.0 - 27.12.2017 - `compare v0.5.1...v0.6.0 <https://github.com/wearehoods/django-ya-model-publisher/compare/v0.5.1...v0.6.0>`_ 

    * refactor permissions and publisher workflow

    * NEW: ``publisher.views.PublisherCmsViewMixin``

    * NEW: ``publisher.admin.VisibilityMixin``

    * bugfix django v1.11 compatibility

    * Expand tests with ``publisher_test_project.publisher_list_app``

* v0.5.1 - 20.12.2017 - `compare v0.5.0...v0.5.1 <https://github.com/wearehoods/django-ya-model-publisher/compare/v0.5.0...v0.5.1>`_ 

    * fix python package (add missing parts)

    * change travis/tox/pytest configuration

    * minor code update

* v0.5.0 - 19.12.2017 - `compare v0.4.1...v0.5.0 <https://github.com/wearehoods/django-ya-model-publisher/compare/v0.4.1...v0.5.0>`_ 

    * Skip official support for python v2.7 and v3.4 (remove from text matrix)

    * Implement "request/reject/accept publishing" workflow with a shot messages and logging

    * Add "request/reject/accept publishing" buttons to Django CMS toolbar for cms pages.

* v0.4.1 - 14.11.2017 - `compare v0.4.0.dev1...v0.4.1 <https://github.com/wearehoods/django-ya-model-publisher/compare/v0.4.0.dev1...v0.4.1>`_ 

    * Refactor test run setup

    * bugfix project name

* v0.4.0.dev1 - 14.11.2017 - `compare v0.3.1...v0.4.0.dev1 <https://github.com/wearehoods/django-ya-model-publisher/compare/v0.3.1...v0.4.0.dev1>`_ 

    * Just create the fork and apply all pull requests from `andersinno/django-model-publisher-ai/pull/14 <https://github.com/andersinno/django-model-publisher-ai/pull/14>`_

-----
links
-----

+---------------+-----------------------------------------------------------+
| Homepage      | `http://github.com/wearehoods/django-ya-model-publisher`_ |
+---------------+-----------------------------------------------------------+
| PyPi.org      | `https://pypi.org/project/django-ya-model-publisher/`_    |
+---------------+-----------------------------------------------------------+
| PyPi (legacy) | `http://pypi.python.org/pypi/django-ya-model-publisher/`_ |
+---------------+-----------------------------------------------------------+

.. _http://github.com/wearehoods/django-ya-model-publisher: http://github.com/wearehoods/django-ya-model-publisher
.. _https://pypi.org/project/django-ya-model-publisher/: https://pypi.org/project/django-ya-model-publisher/
.. _http://pypi.python.org/pypi/django-ya-model-publisher/: http://pypi.python.org/pypi/django-ya-model-publisher/

--------
donation
--------

* `paypal.me/JensDiemer <https://www.paypal.me/JensDiemer>`_

* `Flattr This! <https://flattr.com/submit/auto?uid=jedie&url=https%3A%2F%2Fgithub.com%2Fwearehoods%2Fdjango-ya-model-publisher%2F>`_

* Send `Bitcoins <http://www.bitcoin.org/>`_ to `1823RZ5Md1Q2X5aSXRC5LRPcYdveCiVX6F <https://blockexplorer.com/address/1823RZ5Md1Q2X5aSXRC5LRPcYdveCiVX6F>`_


*(This file is automatically generated by python-creole from ``/README.creole``)*