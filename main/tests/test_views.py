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
from django.urls import reverse
from django.contrib.auth.models import User, Group

from main.models import Book


class IndexViewTests(TestCase):

    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'testpass'
        }
        self.user = User.objects.create_user(**self.credentials)
        self.url = reverse('main:index')

    def test_index_view_get_no_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)
    
    def test_index_view_get_login(self):
        self.client.login(**self.credentials)
        response = self.client.get(self.url)
        self.assertContains(response, self.user.username)


class RegisterViewTests(TestCase):

    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'testpass'
        }
        self.user = User.objects.create_user(**self.credentials)
        self.url = reverse('main:register')

    def test_register_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')
    
    def test_register_view_post_adds_new_user(self):
        response = self.client.post(self.url, {
            'username': 'testuser1',
            'password1': 'sdfkjhsdaofoih',
            'password2': 'sdfkjhsdaofoih'
        })
        self.assertRedirects(response, reverse('main:index'))
        self.assertIn(
            Group.objects.get(name='Student'),
            User.objects.get(username='testuser1').groups.all())


class LibrarianViewTests(TestCase):

    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'testpass'
        }
        self.user = User.objects.create_user(**self.credentials)

        self.librarian_credentials = {
            'username': 'librarian',
            'password': 'testpass'
        }
        self.librarian_user = User.objects.create_user(
            **self.librarian_credentials)
        group = Group.objects.get_or_create(name="Librarian")[0]
        self.librarian_user.groups.add(group)

        self.url = reverse('main:librarian')
    
    def test_librarian_view_get_no_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)
    
    def test_librarian_view_get_login_no_librarian(self):
        self.client.login(**self.credentials)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)
    
    def test_librarian_view_get_login_librarian(self):
        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/librarian.html')
    
    def test_librarian_view_get_no_books(self):
        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertQuerysetEqual(response.context['latest_book_list'], [])
    
    def test_librarian_view_get_three_books(self):
        isbn_list = [
            '9780000000002',
            '9780000000019',
            '9780000000026'
        ]
        for isbn in isbn_list:
            Book.objects.create(
                isbn=isbn, name=isbn, count=1)

        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertQuerysetEqual(response.context['latest_book_list'], [
            '<Book: Book object (9780000000026)>',
            '<Book: Book object (9780000000019)>',
            '<Book: Book object (9780000000002)>'
        ])
    
    def test_librarian_view_get_six_books(self):
        isbn_list = [
            '9780000000002',
            '9780000000019',
            '9780000000026',
            '9780000000033',
            '9780000000040',
            '9780000000057'
        ]
        for isbn in isbn_list:
            Book.objects.create(
                isbn=isbn, name=isbn, count=1)

        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertQuerysetEqual(response.context['latest_book_list'], [
            '<Book: Book object (9780000000057)>',
            '<Book: Book object (9780000000040)>',
            '<Book: Book object (9780000000033)>',
            '<Book: Book object (9780000000026)>',
            '<Book: Book object (9780000000019)>'
        ])


class BookListViewTests(TestCase):

    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'testpass'
        }
        self.user = User.objects.create_user(**self.credentials)

        self.librarian_credentials = {
            'username': 'librarian',
            'password': 'testpass'
        }
        self.librarian_user = User.objects.create_user(
            **self.librarian_credentials)
        group = Group.objects.get_or_create(name="Librarian")[0]
        self.librarian_user.groups.add(group)

        self.url = reverse('main:books')
    
    def test_book_list_view_get_no_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)
    
    def test_book_list_view_get_login_no_librarian(self):
        self.client.login(**self.credentials)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)
    
    def test_book_list_view_get_login_librarian(self):
        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/book_list.html')
    
    def test_book_list_view_get_no_books(self):
        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertQuerysetEqual(response.context['book_list'], [])
    
    def test_book_list_view_get_three_books(self):
        isbn_list = [
            '9780000000002',
            '9780000000019',
            '9780000000026'
        ]
        for isbn in isbn_list:
            Book.objects.create(
                isbn=isbn, name=isbn, count=1)

        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertQuerysetEqual(response.context['book_list'], [
            '<Book: Book object (9780000000026)>',
            '<Book: Book object (9780000000019)>',
            '<Book: Book object (9780000000002)>'
        ])
    
    def test_book_list_view_get_six_books(self):
        isbn_list = [
            '9780000000002',
            '9780000000019',
            '9780000000026',
            '9780000000033',
            '9780000000040',
            '9780000000057'
        ]
        for isbn in isbn_list:
            Book.objects.create(
                isbn=isbn, name=isbn, count=1)

        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertQuerysetEqual(response.context['book_list'], [
            '<Book: Book object (9780000000057)>',
            '<Book: Book object (9780000000040)>',
            '<Book: Book object (9780000000033)>',
            '<Book: Book object (9780000000026)>',
            '<Book: Book object (9780000000019)>',
            '<Book: Book object (9780000000002)>'
        ])


class NewBookViewTests(TestCase):

    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'testpass'
        }
        self.user = User.objects.create_user(**self.credentials)

        self.librarian_credentials = {
            'username': 'librarian',
            'password': 'testpass'
        }
        self.librarian_user = User.objects.create_user(
            **self.librarian_credentials)
        group = Group.objects.get_or_create(name="Librarian")[0]
        self.librarian_user.groups.add(group)

        self.url = reverse('main:new_book')

    def test_new_book_view_get_no_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)
    
    def test_new_book_view_get_login_no_librarian(self):
        self.client.login(**self.credentials)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)
    
    def test_new_book_view_get_login_librarian(self):
        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/new_book.html')
    
    def test_new_book_view_post_adds_new_book(self):
        self.client.login(**self.librarian_credentials)
        response = self.client.post(self.url, {
            'isbn': '9780000000002',
            'name': 'Test Book',
            'count': 1
        })
        self.assertRedirects(response, reverse('main:librarian'))
        self.assertIn(Book.objects.get(isbn='9780000000002').name, 'Test Book')


class BookDetailViewTests(TestCase):

    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'testpass'
        }
        self.user = User.objects.create_user(**self.credentials)

        self.librarian_credentials = {
            'username': 'librarian',
            'password': 'testpass'
        }
        self.librarian_user = User.objects.create_user(
            **self.librarian_credentials)
        group = Group.objects.get_or_create(name="Librarian")[0]
        self.librarian_user.groups.add(group)

        Book.objects.create(
            isbn='9780000000002',
            name='Test Book',
            count=1
        )

        self.url = reverse('main:book_detail', args=['9780000000002'])

    def test_book_detail_view_get_no_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)
    
    def test_book_detail_view_get_login_no_librarian(self):
        self.client.login(**self.credentials)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)
    
    def test_book_detail_view_get_login_librarian(self):
        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/book_detail.html')
