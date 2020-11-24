# Library Management System
# Copyright (C) 2020 Andrey Shmaykhel, Alexander Solovyov, Timur Allayarov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
This module contains tests checking common views in main app.
"""

import os

from django.test import TestCase
from django.urls import reverse

from main.tests.utils import (
    create_test_user, create_admin_user, get_user, test_credentials,
    admin_credentials, base_dir)


class AdminViewTests(TestCase):
    """
    Tests checking admin view functionality.
    """

    def setUp(self):
        create_test_user()
        create_admin_user()

        self.url = reverse('main:admin')

    def test_admin_view_get_no_login(self):
        """
        If user is not authenticated, he is redirected to login page.
        """
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)

    def test_admin_view_get_login_no_admin(self):
        """
        If user is not admin, he is redirected to login page.
        """
        self.client.login(**test_credentials)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)

    def test_admin_view_get_login_admin(self):
        """
        If user is admin, admin page is shown.
        """
        self.client.login(**admin_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/admin.html')


class LogListViewTests(TestCase):
    """
    Tests checking log list view functionality.
    """

    def setUp(self):
        create_test_user()
        create_admin_user()

        self.url = reverse('main:log_list')

    def test_log_list_view_get_no_login(self):
        """
        If user is not authenticated, he is redirected to login page.
        """
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)

    def test_log_list_view_get_login_no_admin(self):
        """
        If user is not admin, he is redirected to login page.
        """
        self.client.login(**test_credentials)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)

    def test_log_list_view_get_login_admin(self):
        """
        If user is admin, log list page is shown.
        """
        self.client.login(**admin_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/logentry_list.html')


class UserListViewTests(TestCase):
    """
    Tests checking user list view functionality.
    """

    def setUp(self):
        create_test_user()
        create_admin_user()

        self.url = reverse('main:user_list')

    def test_user_list_view_get_no_login(self):
        """
        If user is not authenticated, he is redirected to login page.
        """
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)

    def test_user_list_view_get_login_no_admin(self):
        """
        If user is not admin, he is redirected to login page.
        """
        self.client.login(**test_credentials)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)

    def test_user_list_view_get_login_admin(self):
        """
        If user is admin, user list page is shown.
        """
        self.client.login(**admin_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/user_list.html')


class AdminProfileViewTests(TestCase):
    """
    Tests checking admin profile view functionality.
    """

    def setUp(self):
        user = create_test_user()
        create_admin_user()

        self.url = reverse('main:admin_profile', args=[user.id])

    def test_admin_profile_view_get_no_login(self):
        """
        If user is not authenticated, he is redirected to login page.
        """
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)

    def test_admin_profile_view_get_login_no_admin(self):
        """
        If user is not admin, he is redirected to login page.
        """
        self.client.login(**test_credentials)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)

    def test_admin_profile_view_get_login_admin(self):
        """
        If user is admin, admin profile page is shown.
        """
        self.client.login(**admin_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/admin_profile.html')


class BlockUserViewTests(TestCase):
    """
    Tests checking block user view functionality.
    """

    def setUp(self):
        self.user = create_test_user()
        self.admin = create_admin_user()

        self.url = reverse('main:block_user', args=[self.user.id])
        self.admin_url = reverse('main:block_user', args=[self.admin.id])

    def test_block_user_view_get_no_login(self):
        """
        If user is not authenticated, he is redirected to login page.
        """
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)

    def test_block_user_view_get_login_no_admin(self):
        """
        If user is not admin, he is redirected to login page.
        """
        self.client.login(**test_credentials)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)

    def test_block_user_view_get_login_admin_active_user(self):
        """
        If user is admin and block user is active, block user confirmation page
        is shown.
        """
        self.client.login(**admin_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/block_user.html')

    def test_block_user_view_get_login_admin_inactive_user(self):
        """
        If user is admin and block user is inactive, he is redirected to admin
        profile page.
        """
        self.user.is_active = False
        self.user.save()
        self.client.login(**admin_credentials)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:admin_profile', args=[self.user.id]))

    def test_block_user_view_get_login_admin_self(self):
        """
        If user is admin and block user is inactive, he is redirected to admin
        profile page.
        """
        self.client.login(**admin_credentials)
        response = self.client.get(self.admin_url)
        self.assertRedirects(
            response,
            reverse('main:admin_profile', args=[self.admin.id]))

    def test_block_user_view_post(self):
        """
        If POST request is sent, user is blocked
        """
        self.client.login(**admin_credentials)
        response = self.client.post(self.url, {})
        self.assertRedirects(
            response,
            reverse('main:admin_profile', args=[self.user.id]))
        self.assertFalse(get_user('testuser').is_active)


class UnblockUserViewTests(TestCase):
    """
    Tests checking block user view functionality.
    """

    def setUp(self):
        self.user = create_test_user()
        self.user.is_active = False
        self.user.save()
        create_admin_user()

        self.url = reverse('main:unblock_user', args=[self.user.id])

    def test_unblock_user_view_get_no_login(self):
        """
        If user is not authenticated, he is redirected to login page.
        """
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)

    def test_unblock_user_view_get_login_no_admin(self):
        """
        If user is not admin, he is redirected to login page.
        """
        self.client.login(**test_credentials)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)

    def test_unblock_user_view_get_login_admin_inactive_user(self):
        """
        If user is admin and block user is active, block user confirmation page
        is shown.
        """
        self.client.login(**admin_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/unblock_user.html')

    def test_unblock_user_view_get_login_admin_active_user(self):
        """
        If user is admin and block user is active, he is redirected to admin
        profile page.
        """
        self.user.is_active = True
        self.user.save()
        self.client.login(**admin_credentials)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:admin_profile', args=[self.user.id]))

    def test_unblock_user_view_post(self):
        """
        If POST request is sent, user is blocked
        """
        self.client.login(**admin_credentials)
        response = self.client.post(self.url, {})
        self.assertRedirects(
            response,
            reverse('main:admin_profile', args=[self.user.id]))
        self.assertTrue(get_user('testuser').is_active)


class SelectThemeViewTests(TestCase):
    """
    Tests checking select theme view functionality.
    """

    def setUp(self):
        create_admin_user()

        self.path = base_dir + '/main/static/main/css/active.css'
        if os.path.exists(self.path):
            os.remove(self.path)

        self.url = reverse('main:select_theme')

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)
        os.symlink('default.css', self.path)

    def test_select_theme_view_get_no_login(self):
        """
        If user is not authenticated, he is redirected to login page.
        """
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)

    def test_select_theme_view_get_login_no_admin(self):
        """
        If user is not admin, he is redirected to login page.
        """
        self.client.login(**test_credentials)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)

    def test_select_theme_view_get_login_admin(self):
        """
        If user is admin, select theme page is shown.
        """
        self.client.login(**admin_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/select_theme.html')

    def test_select_theme_view_post_set_dark_theme(self):
        """
        If POST request is sent and dark theme is selected, it is applied.
        """
        self.client.login(**admin_credentials)
        response = self.client.post(self.url, {'theme': 'dark'})
        self.assertRedirects(
            response,
            reverse('main:admin'))
        self.assertEqual(os.readlink(self.path), 'dark.css')

    def test_select_theme_view_post_set_default_theme(self):
        """
        If POST request is sent and default theme is selected, it is applied.
        """
        self.client.login(**admin_credentials)
        response = self.client.post(self.url, {'theme': 'default'})
        self.assertRedirects(
            response,
            reverse('main:admin'))
        self.assertEqual(os.readlink(self.path), 'default.css')
