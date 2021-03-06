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
This module contains tests of models in main app.
"""

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from main.models import Book

from .utils import student_credentials, create_student_lease


class BookModelTests(TestCase):
    """
    Tests checking book model.
    """

    def setUp(self):
        self.book1 = Book.objects.create(
            isbn='9780000000002',
            name='Test Book',
            count=2)

        self.book2 = Book.objects.create(
            isbn='9780000000019',
            name='Test Book 2',
            count=0)

        student_user = get_user_model().objects.create_user(
            **student_credentials)
        group = Group.objects.get_or_create(name="Student")[0]
        student_user.groups.add(group)

    def test_book_is_active_on_active_book(self):
        """
        If book is active, true is returned.
        """
        self.assertTrue(self.book1.is_active())

    def test_book_is_active_on_inactive_book(self):
        """
        If book is active, false is returned.
        """
        self.assertFalse(self.book2.is_active())

    def test_book_available_count_when_two_available(self):
        """
        If 2 books are available, 2 is returned.
        """
        self.assertEqual(self.book1.available_count(), 2)

    def test_book_available_count_when_one_available(self):
        """
        If 1 book is available, 1 is returned.
        """
        create_student_lease('9780000000002')
        self.assertEqual(self.book1.available_count(), 1)

    def test_book_available_count_when_none_available(self):
        """
        If no books are available, 0 is returned.
        """
        for _ in range(2):
            create_student_lease('9780000000002')
        self.assertEqual(self.book1.available_count(), 0)

    def test_book_is_available_when_two_available(self):
        """
        If 2 books are available, true is returned.
        """
        self.assertTrue(self.book1.is_available())

    def test_book_is_available_when_one_available(self):
        """
        If 1 book is available, true is returned.
        """
        create_student_lease('9780000000002')
        self.assertTrue(self.book1.is_available())

    def test_book_is_available_when_none_available(self):
        """
        If no books are available, false is returned.
        """
        for _ in range(2):
            create_student_lease('9780000000002')
        self.assertFalse(self.book1.is_available())


class LeaseModelTests(TestCase):
    """
    Tests checking lease model.
    """

    def setUp(self):
        Book.objects.create(
            isbn='9780000000002',
            name='Test Book',
            count=2)

        student_user = get_user_model().objects.create_user(
            **student_credentials)
        group = Group.objects.get_or_create(name="Student")[0]
        student_user.groups.add(group)

        self.lease = create_student_lease('9780000000002')

    def test_lease_is_active_on_active_lease(self):
        """
        If lease is active, true is returned.
        """
        self.assertTrue(self.lease.is_active())

    def test_lease_is_active_on_returned_lease(self):
        """
        If lease is returned, false is returned.
        """
        self.lease.return_date = timezone.now()
        self.lease.save()
        self.assertFalse(self.lease.is_active())
