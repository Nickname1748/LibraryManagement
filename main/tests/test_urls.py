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

from main import views


class UrlsTests(SimpleTestCase):
    """
    Tests checking URL to view resolution.
    """

    def test_index_view_resolves(self):
        url = reverse('main:index')
        self.assertEqual(resolve(url).func, views.index)

    def test_register_view_resolves(self):
        url = reverse('main:register')
        self.assertEqual(resolve(url).func, views.register)
    
    def test_customer_view_resolves(self):
        url = reverse('main:customer')
        self.assertEqual(resolve(url).func, views.customer)

    def test_librarian_view_resolves(self):
        url = reverse('main:librarian')
        self.assertEqual(resolve(url).func, views.librarian)

    def test_new_book_view_resolves(self):
        url = reverse('main:new_book')
        self.assertEqual(resolve(url).func, views.new_book)

    def test_book_list_view_resolves(self):
        url = reverse('main:books')
        self.assertEqual(resolve(url).func.view_class, views.BookListView)

    def test_book_detail_view_resolves(self):
        url = reverse('main:book_detail', args=['9780000000002'])
        self.assertEqual(resolve(url).func.view_class, views.BookDetailView)
    
    def test_new_lease_view_resolves(self):
        url = reverse('main:new_lease', args=['9780000000002'])
        self.assertEqual(resolve(url).func, views.new_lease)
    
    def test_return_lease_view_resolves(self):
        url = reverse(
            'main:return_lease',
            args=['70442b70-adec-4b4d-b49e-7af85edee576'])
        self.assertEqual(resolve(url).func, views.return_lease)

    def test_lease_list_view_resolves(self):
        url = reverse('main:leases')
        self.assertEqual(resolve(url).func.view_class, views.LeaseListView)

    def test_lease_detail_view_resolves(self):
        url = reverse(
            'main:lease_detail',
            args=['70442b70-adec-4b4d-b49e-7af85edee576'])
        self.assertEqual(resolve(url).func.view_class, views.LeaseDetailView)
