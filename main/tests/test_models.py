"""
Library Management System
Copyright (C) 2020 Andrey Shmaykhel, Alexander Solovyov, Timur Allayarov

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from django.test import TestCase

from main.models import Book


class BookModelTests(TestCase):

    def setUp(self):
        self.book1 = Book.objects.create(
            isbn='9780000000002',
            name='Test Book',
            count=1
        )

        self.book2 = Book.objects.create(
            isbn='9780000000019',
            name='Test Book 2',
            count=0
        )
    
    def test_book_is_active_on_active_book(self):
        self.assertTrue(self.book1.is_active())
    
    def test_book_is_active_on_inactive_book(self):
        self.assertFalse(self.book2.is_active())
