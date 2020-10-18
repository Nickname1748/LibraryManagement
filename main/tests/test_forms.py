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
This module contains tests if forms in main app.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone

from main.forms import BookCreationForm, LeaseCreationForm
from main.models import Book, Lease


class BookCreationFormTests(TestCase):
    """
    Tests checking book creation form validation.
    """

    def test_book_creation_form_valid_data_isbn_13(self):
        """
        If valid data is sent using ISBN-13 format, form is valid.
        """
        form = BookCreationForm(data={
            'isbn': '9780000000002',
            'name': 'Test Book',
            'count': 1
        })
        self.assertTrue(form.is_valid())

    def test_book_creation_form_valid_data_isbn_10(self):
        """
        If valid data is sent using ISBN-10 format, form is valid.
        """
        form = BookCreationForm(data={
            'isbn': '0000000000',
            'name': 'Test Book',
            'count': 1
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['isbn'], '9780000000002')

    def test_book_creation_form_no_data(self):
        """
        If no data is sent, form is invalid.
        """
        form = BookCreationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3)

    def test_book_creation_form_no_isbn(self):
        """
        If no isbn is sent, form is invalid.
        """
        form = BookCreationForm(data={
            'name': 'Test Book',
            'count': 1
        })
        self.assertFalse(form.is_valid())

    def test_book_creation_form_invalid_isbn(self):
        """
        If isbn is invalid, form is invalid.
        """
        form = BookCreationForm(data={
            'isbn': '9780000000001',
            'name': 'Test Book',
            'count': 1
        })
        self.assertFalse(form.is_valid())

    def test_book_creation_form_no_name(self):
        """
        If no book name is sent, form is invalid.
        """
        form = BookCreationForm(data={
            'isbn': '9780000000002',
            'count': 1
        })
        self.assertFalse(form.is_valid())

    def test_book_creation_form_no_count(self):
        """
        If no book count is sent, form is invalid.
        """
        form = BookCreationForm(data={
            'isbn': '9780000000002',
            'name': 'Test Book'
        })
        self.assertFalse(form.is_valid())

    def test_book_creation_form_count_is_zero(self):
        """
        If book count is 0, form is invalid.
        """
        form = BookCreationForm(data={
            'isbn': '9780000000002',
            'name': 'Test Book',
            'count': 0
        })
        self.assertFalse(form.is_valid())


class LeaseCreationFormTests(TestCase):
    """
    Tests checking lease creation form validation.
    """

    def setUp(self):
        Book.objects.create(
            isbn='9780000000002',
            name='Test Book',
            count=1)

        Book.objects.create(
            isbn='9780000000019',
            name='Test Book 2',
            count=0)

        self.student_credentials = {
            'username': 'student1',
            'password': 'testpass'
        }
        self.student_user = get_user_model().objects.create_user(
            **self.student_credentials)
        group = Group.objects.get_or_create(name="Student")[0]
        self.student_user.groups.add(group)

    def test_lease_creation_form_valid_data(self):
        """
        If valid data is sent, form is valid.
        """
        form = LeaseCreationForm(data={
            'student': self.student_user.id,
            'book': '9780000000002',
            'expire_date': str(
                (timezone.now()+timezone.timedelta(days=30)).date())
        })
        self.assertTrue(form.is_valid())

    def test_lease_creation_form_no_data(self):
        """
        If no data is sent, form is invalid.
        """
        form = LeaseCreationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3)

    def test_lease_creation_form_no_student(self):
        """
        If no student is sent, form is invalid.
        """
        form = LeaseCreationForm(data={
            'book': '9780000000002',
            'expire_date': str(
                (timezone.now()+timezone.timedelta(days=30)).date())
        })
        self.assertFalse(form.is_valid())

    def test_lease_creation_form_inexistent_student(self):
        """
        If student does not exist, form is invalid.
        """
        form = LeaseCreationForm(data={
            'student': self.student_user.id+1,
            'book': '9780000000002',
            'expire_date': str(
                (timezone.now()+timezone.timedelta(days=30)).date())
        })
        self.assertFalse(form.is_valid())

    def test_lease_creation_form_no_book(self):
        """
        If no book is sent, form is invalid.
        """
        form = LeaseCreationForm(data={
            'student': self.student_user.id,
            'expire_date': str(
                (timezone.now()+timezone.timedelta(days=30)).date())
        })
        self.assertFalse(form.is_valid())

    def test_lease_creation_form_inexistent_book(self):
        """
        If book does not exist, form is invalid.
        """
        form = LeaseCreationForm(data={
            'student': self.student_user.id,
            'book': '9780000000026',
            'expire_date': str(
                (timezone.now()+timezone.timedelta(days=30)).date())
        })
        self.assertFalse(form.is_valid())

    def test_lease_creation_form_inactive_book(self):
        """
        If book is inactive, form is invalid.
        """
        form = LeaseCreationForm(data={
            'student': self.student_user.id,
            'book': '9780000000019',
            'expire_date': str(
                (timezone.now()+timezone.timedelta(days=30)).date())
        })
        self.assertFalse(form.is_valid())

    def test_lease_creation_form_unavailable_book(self):
        """
        If book is unavailable, form is invalid.
        """
        Lease.objects.create(
            student=get_user_model().objects.get_by_natural_key(
                self.student_credentials['username']),
            book=Book.objects.get(pk='9780000000002'),
            expire_date=timezone.now() + timezone.timedelta(days=30))

        form = LeaseCreationForm(data={
            'student': self.student_user.id,
            'book': '9780000000002',
            'expire_date': str(
                (timezone.now()+timezone.timedelta(days=30)).date())
        })
        self.assertFalse(form.is_valid())

    def test_lease_creation_form_no_expire_date(self):
        """
        If student does not exist, form is invalid.
        """
        form = LeaseCreationForm(data={
            'student': self.student_user.id,
            'book': '9780000000002'
        })
        self.assertFalse(form.is_valid())

    def test_lease_creation_form_expire_date_in_past(self):
        """
        If student does not exist, form is invalid.
        """
        form = LeaseCreationForm(data={
            'student': self.student_user.id,
            'book': '9780000000002',
            'expire_date': str(
                (timezone.now()-timezone.timedelta(days=30)).date())
        })
        self.assertFalse(form.is_valid())
