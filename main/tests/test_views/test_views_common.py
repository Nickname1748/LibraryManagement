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
    check_user_in_group, check_user_is_active, create_inactive_librarian_user,
    create_test_user, create_admin_user, create_librarian_user,
    create_student_user, generate_activation_key, test_credentials,
    admin_credentials, librarian_credentials, student_credentials)


class IndexViewTests(TestCase):
    """
    Tests checking index view functionality.
    """

    def setUp(self):
        create_admin_user()
        create_librarian_user()
        create_student_user()

        self.url = reverse('main:index')

    def test_index_view_get_no_login(self):
        """
        If user is not authenticated, he is redirected to login page.
        """
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)

    def test_index_view_get_login_admin(self):
        """
        If user is admin, he is redirected to admin page.
        """
        self.client.login(**admin_credentials)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('main:admin'))

    def test_index_view_get_login_librarian(self):
        """
        If user is librarian, he is redirected to librarian page.
        """
        self.client.login(**librarian_credentials)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('main:librarian'))

    def test_index_view_get_login_student(self):
        """
        If user is student, he is redirected to student page.
        """
        self.client.login(**student_credentials)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('main:student'))


class RegisterViewTests(TestCase):
    """
    Tests checking register view functionality.
    """

    def setUp(self):
        self.url = reverse('main:register')

    def test_register_view_get(self):
        """
        If GET request is sent, register form is shown.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'django_registration/registration_form.html')

    def test_register_view_post_adds_new_user(self):
        """
        If valid POST request is sent, new Student user is added.
        """
        response = self.client.post(self.url, {
            'username': 'testuser1',
            'first_name': 'Test',
            'last_name': 'Testov',
            'email': 'test@example.com',
            'password1': 'sdfkjhsdaofoih',
            'password2': 'sdfkjhsdaofoih'
        })
        self.assertRedirects(response, reverse('main:registration_complete'))
        self.assertTrue(check_user_in_group('testuser1', 'Student'))

    def test_register_view_post_invalid_fails(self):
        """
        If invalid POST request is sent, errors are shown.
        """
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.context['form'].errors), 0)


class LibrarianRegisterViewTests(TestCase):
    """
    Tests checking librarian registration view functionality.
    """

    def setUp(self):
        create_test_user()
        create_admin_user()

        self.url = reverse('main:register_librarian')

    def test_libarian_register_view_get_no_login(self):
        """
        If user is not authenticated, he is redirected to login page.
        """
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)

    def test_libarian_register_view_get_login_no_admin(self):
        """
        If user is not admin, he is redirected to login page.
        """
        self.client.login(**test_credentials)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)

    def test_librarian_register_view_get_login_admin(self):
        """
        If user is admin, librarian register form is shown.
        """
        self.client.login(**admin_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'main/librarian_registration.html')

    def test_librarian_register_view_post_adds_new_user(self):
        """
        If valid POST request is sent, new librarian user is added.
        """
        self.client.login(**admin_credentials)
        response = self.client.post(self.url, {
            'username': 'librarian',
            'first_name': 'Test',
            'last_name': 'Testov',
            'email': 'librarian@example.com'
        })
        self.assertRedirects(response, reverse('main:admin'))
        self.assertTrue(check_user_in_group('librarian', 'Librarian'))
        self.assertFalse(check_user_is_active('librarian'))

    def test_librarian_register_view_post_invalid_fails(self):
        """
        If invalid POST request is sent, errors are shown.
        """
        self.client.login(**admin_credentials)
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.context['form'].errors), 0)


class LibrarianActivationViewTests(TestCase):
    """
    Tests checking librarian activation view functionality.
    """

    def setUp(self):
        librarian = create_inactive_librarian_user()
        activation_key = generate_activation_key(librarian)

        self.url = reverse('main:activate_librarian', args=[activation_key])

    def test_librarian_activation_view_get(self):
        """
        If GET request is sent, user is redirected to password change page.
        """
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('main:password_change'))
        self.assertTrue(check_user_is_active('librarian'))
