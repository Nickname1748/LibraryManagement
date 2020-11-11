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
This module contains tests of URL matching in main app.
"""

from django_registration.backends.activation import views as registration_views

from django.test import SimpleTestCase
from django.urls import reverse, resolve
from django.contrib.auth import views as auth_views

from main import views


class UrlsTests(SimpleTestCase):
    """
    Tests checking URL to view resolution.
    """

    def test_index_view_resolves(self):
        """
        main:index URL resolves to index view.
        """
        url = reverse('main:index')
        self.assertEqual(resolve(url).func, views.index)

    def test_profile_view_resolves(self):
        """
        main:profile URL resolves to profile view.
        """
        url = reverse('main:profile')
        self.assertEqual(resolve(url).func, views.profile)

    def test_admin_view_resolves(self):
        """
        main:admin URL resolves to admin view.
        """
        url = reverse('main:admin')
        self.assertEqual(resolve(url).func, views.admin)

    def test_register_librarian_view_resolves(self):
        """
        main:register_librarian URL resolves to register librarian view.
        """
        url = reverse('main:register_librarian')
        self.assertEqual(
            resolve(url).func.view_class, views.LibrarianRegisterView)

    def test_activate_librarian_view_resolves(self):
        """
        main:activate_librarian URL resolves to activate librarian view.
        """
        url = reverse(
            'main:activate_librarian',
            args=[
                'IoelYjQi:1kckPR:JHTTCehMd752yaNJyMJY4oChloxBCkd7hxKepVbjtR4'
            ])
        self.assertEqual(
            resolve(url).func.view_class, views.LibrarianActivationView)

    def test_student_view_resolves(self):
        """
        main:student URL resolves to student view.
        """
        url = reverse('main:student')
        self.assertEqual(resolve(url).func, views.student)

    def test_librarian_view_resolves(self):
        """
        main:librarian URL resolves to librarian view.
        """
        url = reverse('main:librarian')
        self.assertEqual(resolve(url).func, views.librarian)

    def test_new_book_view_resolves(self):
        """
        main:new_book URL resolves to new_book view.
        """
        url = reverse('main:new_book')
        self.assertEqual(resolve(url).func, views.new_book)

    def test_book_list_view_resolves(self):
        """
        main:books URL resolves to BookListView view.
        """
        url = reverse('main:books')
        self.assertEqual(resolve(url).func.view_class, views.BookListView)

    def test_book_detail_view_resolves(self):
        """
        main:book_detail URL resolves to BookDetailView view.
        """
        url = reverse('main:book_detail', args=['9780000000002'])
        self.assertEqual(resolve(url).func.view_class, views.BookDetailView)

    def test_new_lease_view_resolves(self):
        """
        main:new_lease URL resolves to new_lease view.
        """
        url = reverse('main:new_lease', args=['9780000000002'])
        self.assertEqual(resolve(url).func, views.new_lease)

    def test_lease_list_view_resolves(self):
        """
        main:leases URL resolves to LeaseListView view.
        """
        url = reverse('main:leases')
        self.assertEqual(resolve(url).func.view_class, views.LeaseListView)

    def test_return_lease_view_resolves(self):
        """
        main:return_lease URL resolves to return_lease view.
        """
        url = reverse(
            'main:return_lease',
            args=['70442b70-adec-4b4d-b49e-7af85edee576'])
        self.assertEqual(resolve(url).func, views.return_lease)

    def test_lease_detail_view_resolves(self):
        """
        main:lease_detail URL resolves to LeaseDetailView view.
        """
        url = reverse(
            'main:lease_detail',
            args=['70442b70-adec-4b4d-b49e-7af85edee576'])
        self.assertEqual(resolve(url).func.view_class, views.LeaseDetailView)

    def test_xlsx_report_view_resolves(self):
        """
        main:xlsx_report URL resolves to XLSX report view.
        """
        url = reverse('main:xlsx_report')
        self.assertEqual(resolve(url).func, views.xlsx_report)


class AuthUrlsTests(SimpleTestCase):
    """
    Tests checking auth URL to view resolution.
    """

    def test_login_view_resolves(self):
        """
        main:login URL resolves to login view.
        """
        url = reverse('main:login')
        self.assertEqual(resolve(url).func.view_class, auth_views.LoginView)

    def test_logout_view_resolves(self):
        """
        main:logout URL resolves to logout view.
        """
        url = reverse('main:logout')
        self.assertEqual(resolve(url).func.view_class, auth_views.LogoutView)

    def test_password_change_view_resolves(self):
        """
        main:password_change URL resolves to password change view.
        """
        url = reverse('main:password_change')
        self.assertEqual(
            resolve(url).func.view_class, auth_views.PasswordChangeView)

    def test_password_change_done_view_resolves(self):
        """
        main:password_change_done URL resolves to password change done
        view.
        """
        url = reverse('main:password_change_done')
        self.assertEqual(
            resolve(url).func.view_class, auth_views.PasswordChangeDoneView)

    def test_password_reset_view_resolves(self):
        """
        main:password_reset URL resolves to password reset view.
        """
        url = reverse('main:password_reset')
        self.assertEqual(
            resolve(url).func.view_class, auth_views.PasswordResetView)

    def test_password_reset_done_view_resolves(self):
        """
        main:password_reset_done URL resolves to password reset done
        view.
        """
        url = reverse('main:password_reset_done')
        self.assertEqual(
            resolve(url).func.view_class, auth_views.PasswordResetDoneView)

    def test_password_reset_confirm_view_resolves(self):
        """
        main:password_reset_confirm URL resolves to password reset
        confirm view.
        """
        url = reverse(
            'main:password_reset_confirm',
            args=[
                'MSc',
                'ad67s6-265a90812886dadfd00ce774392dd756'
            ])
        self.assertEqual(
            resolve(url).func.view_class, auth_views.PasswordResetConfirmView)

    def test_password_reset_complete_view_resolves(self):
        """
        main:password_reset_complete URL resolves to password reset
        complete view.
        """
        url = reverse('main:password_reset_complete')
        self.assertEqual(
            resolve(url).func.view_class, auth_views.PasswordResetCompleteView)


class RegistrationUrlsTests(SimpleTestCase):
    """
    Tests checking auth URL to view resolution.
    """

    def test_activate_view_resolves(self):
        """
        main:activate URL resolves to activation_confirm view.
        """
        url = reverse(
            'main:activate',
            args=[
                'IoelYjQi:1kckPR:JHTTCehMd752yaNJyMJY4oChloxBCkd7hxKepVbjtR4'
            ])
        self.assertEqual(
            resolve(url).func.view_class, registration_views.ActivationView)

    def test_register_view_resolves(self):
        """
        main:register URL resolves to register view.
        """
        url = reverse('main:register')
        self.assertEqual(resolve(url).func.view_class, views.RegisterView)
