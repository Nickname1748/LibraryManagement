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

from django.test import SimpleTestCase
from django.urls import reverse, resolve

from main.views import index, register, librarian, new_book
from main.views import BookListView, BookDetailView


class UrlsTests(SimpleTestCase):

    def test_index_view_resolves(self):
        url = reverse('main:index')
        self.assertEqual(resolve(url).func, index)

    def test_register_view_resolves(self):
        url = reverse('main:register')
        self.assertEqual(resolve(url).func, register)

    def test_librarian_view_resolves(self):
        url = reverse('main:librarian')
        self.assertEqual(resolve(url).func, librarian)

    def test_new_book_view_resolves(self):
        url = reverse('main:new_book')
        self.assertEqual(resolve(url).func, new_book)

    def test_book_list_view_resolves(self):
        url = reverse('main:books')
        self.assertEqual(resolve(url).func.view_class, BookListView)

    def test_book_detail_view_resolves(self):
        url = reverse('main:book_detail', args=['9780000000002'])
        self.assertEqual(resolve(url).func.view_class, BookDetailView)
