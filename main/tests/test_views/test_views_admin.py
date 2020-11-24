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

from django.test import TestCase
from django.urls import reverse

from main.tests.utils import (
    create_test_user, create_admin_user, test_credentials, admin_credentials)


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
