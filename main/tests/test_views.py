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

import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from main.models import Book, Lease


class IndexViewTests(TestCase):
    """
    Tests checking index view functionality.
    """

    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'testpass'
        }
        self.user = get_user_model().objects.create_user(**self.credentials)
        self.url = reverse('main:index')

    def test_index_view_get_no_login(self):
        """
        If user is not authenticated, he is redirected to login page.
        """
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)
    
    def test_index_view_get_login(self):
        """
        If user is authenticated, his username is shown.
        """
        self.client.login(**self.credentials)
        response = self.client.get(self.url)
        self.assertContains(response, self.user.username)


class RegisterViewTests(TestCase):
    """
    Tests checking register view functionality.
    """

    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'testpass'
        }
        self.user = get_user_model().objects.create_user(**self.credentials)
        self.url = reverse('main:register')

    def test_register_view_get(self):
        """
        If GET request is sent, register form is shown.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')
    
    def test_register_view_post_adds_new_user(self):
        """
        If valid POST request is sent, new Student user is added.
        """
        response = self.client.post(self.url, {
            'username': 'testuser1',
            'password1': 'sdfkjhsdaofoih',
            'password2': 'sdfkjhsdaofoih'
        })
        self.assertRedirects(response, reverse('main:index'))
        self.assertIn(
            Group.objects.get(name='Student'),
            get_user_model().objects.get(username='testuser1').groups.all())


class StudentViewTests(TestCase):
    """
    Tests checking student view functionality.
    """

    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'testpass'
        }
        self.user = get_user_model().objects.create_user(**self.credentials)

        self.student_credentials = {
            'username': 'student1',
            'password': 'testpass'
        }
        self.student_user = get_user_model().objects.create_user(
            **self.student_credentials)
        group = Group.objects.get_or_create(name="Student")[0]
        self.student_user.groups.add(group)

        self.another_student_credentials = {
            'username': 'student2',
            'password': 'testpass'
        }
        self.another_student_user = get_user_model().objects.create_user(
            **self.another_student_credentials)
        group = Group.objects.get_or_create(name="Student")[0]
        self.another_student_user.groups.add(group)

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

        self.url = reverse('main:student')
    
    def test_student_view_get_no_login(self):
        """
        If user is not authenticated, he is redirected to login page.
        """
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)
    
    def test_student_view_get_login_no_student(self):
        """
        If user is not student, he is redirected to login page.
        """
        self.client.login(**self.credentials)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)
    
    def test_student_view_get_login_student(self):
        """
        If user is student, student page is shown.
        """
        self.client.login(**self.student_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/student.html')
    
    def test_student_view_get_no_leases(self):
        """
        If no leases exist, no leases are shown.
        """
        self.client.login(**self.student_credentials)
        response = self.client.get(self.url)
        self.assertQuerysetEqual(response.context['active_lease_list'], [])
        
    def test_student_view_get_six_leases(self):
        """
        If 6 leases exist, all 6 leases are shown.
        """
        isbn_list = [
            '9780000000002',
            '9780000000019',
            '9780000000026',
            '9780000000033',
            '9780000000040',
            '9780000000057'
        ]
        for isbn in isbn_list:
            Lease.objects.create(
                student=get_user_model().objects.get_by_natural_key(
                    self.student_credentials['username']),
                book=Book.objects.get(pk=isbn),
                expire_date=timezone.now() + timezone.timedelta(days=30))

        self.client.login(**self.student_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.context['active_lease_list'].count(), 6)
        self.assertEqual(
            response.context['active_lease_list'][0].book.isbn,
            '9780000000002')
        self.assertEqual(
            response.context['active_lease_list'][5].book.isbn,
            '9780000000057')
    
    def test_student_view_get_anothers_leases(self):
        """
        If only another student leases exist, no leases are shown.
        """
        isbn_list = [
            '9780000000002',
            '9780000000019',
            '9780000000026',
            '9780000000033',
            '9780000000040',
            '9780000000057'
        ]
        for isbn in isbn_list:
            Lease.objects.create(
                student=get_user_model().objects.get_by_natural_key(
                    self.another_student_credentials['username']),
                book=Book.objects.get(pk=isbn),
                expire_date=timezone.now() + timezone.timedelta(days=30))

        self.client.login(**self.student_credentials)
        response = self.client.get(self.url)
        self.assertQuerysetEqual(response.context['active_lease_list'], [])
    
    def test_student_view_get_ones_and_anothers_leases(self):
        """
        If 3 current student leases exist, only these 3 leases are
        shown.
        """
        isbn_list = [
            '9780000000002',
            '9780000000019',
            '9780000000026'
        ]
        another_isbn_list = [
            '9780000000033',
            '9780000000040',
            '9780000000057'
        ]
        for isbn in isbn_list:
            Lease.objects.create(
                student=get_user_model().objects.get_by_natural_key(
                    self.student_credentials['username']),
                book=Book.objects.get(pk=isbn),
                expire_date=timezone.now() + timezone.timedelta(days=30))
        for isbn in another_isbn_list:
            Lease.objects.create(
                student=get_user_model().objects.get_by_natural_key(
                    self.another_student_credentials['username']),
                book=Book.objects.get(pk=isbn),
                expire_date=timezone.now() + timezone.timedelta(days=30))

        self.client.login(**self.student_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.context['active_lease_list'].count(), 3)
        self.assertEqual(
            response.context['active_lease_list'][0].book.isbn,
            '9780000000002')
        self.assertEqual(
            response.context['active_lease_list'][2].book.isbn,
            '9780000000026')
    
    def test_student_view_get_returned_leases(self):
        """
        If all leases are returned, no leases are shown.
        """
        isbn_list = [
            '9780000000002',
            '9780000000019',
            '9780000000026',
            '9780000000033',
            '9780000000040',
            '9780000000057'
        ]
        for isbn in isbn_list:
            Lease.objects.create(
                student=get_user_model().objects.get_by_natural_key(
                    self.student_credentials['username']),
                book=Book.objects.get(pk=isbn),
                expire_date=timezone.now() + timezone.timedelta(days=30),
                return_date=timezone.now())

        self.client.login(**self.student_credentials)
        response = self.client.get(self.url)
        self.assertQuerysetEqual(response.context['active_lease_list'], [])
    
    def test_student_view_get_active_and_returned_leases(self):
        """
        If 3 active leases exist, only these 3 leases are shown.
        """
        isbn_list = [
            '9780000000002',
            '9780000000019',
            '9780000000026'
        ]
        another_isbn_list = [
            '9780000000033',
            '9780000000040',
            '9780000000057'
        ]
        for isbn in isbn_list:
            Lease.objects.create(
                student=get_user_model().objects.get_by_natural_key(
                    self.student_credentials['username']),
                book=Book.objects.get(pk=isbn),
                expire_date=timezone.now() + timezone.timedelta(days=30))
        for isbn in another_isbn_list:
            Lease.objects.create(
                student=get_user_model().objects.get_by_natural_key(
                    self.student_credentials['username']),
                book=Book.objects.get(pk=isbn),
                expire_date=timezone.now() + timezone.timedelta(days=30),
                return_date=timezone.now())

        self.client.login(**self.student_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.context['active_lease_list'].count(), 3)
        self.assertEqual(
            response.context['active_lease_list'][0].book.isbn,
            '9780000000002')
        self.assertEqual(
            response.context['active_lease_list'][2].book.isbn,
            '9780000000026')
        
    def test_student_view_get_leases_ordered(self):
        """
        Leases are shown in expire date order.
        """
        isbn_list = [
            '9780000000002',
            '9780000000019',
            '9780000000026',
            '9780000000033',
            '9780000000040',
            '9780000000057'
        ]
        for i, isbn in enumerate(isbn_list):
            Lease.objects.create(
                student=get_user_model().objects.get_by_natural_key(
                    self.student_credentials['username']),
                book=Book.objects.get(pk=isbn),
                expire_date=
                    timezone.now()
                    + timezone.timedelta(days=30-i))

        self.client.login(**self.student_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.context['active_lease_list'].count(), 6)
        self.assertEqual(
            response.context['active_lease_list'][0].book.isbn,
            '9780000000057')
        self.assertEqual(
            response.context['active_lease_list'][3].book.isbn,
            '9780000000026')
        self.assertEqual(
            response.context['active_lease_list'][5].book.isbn,
            '9780000000002')


class LibrarianViewTests(TestCase):
    """
    Tests checking librarian view functionality.
    """

    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'testpass'
        }
        self.user = get_user_model().objects.create_user(**self.credentials)

        self.student_credentials = {
            'username': 'student1',
            'password': 'testpass'
        }
        self.student_user = get_user_model().objects.create_user(
            **self.student_credentials)
        group = Group.objects.get_or_create(name="Student")[0]
        self.student_user.groups.add(group)

        self.librarian_credentials = {
            'username': 'librarian',
            'password': 'testpass'
        }
        self.librarian_user = get_user_model().objects.create_user(
            **self.librarian_credentials)
        group = Group.objects.get_or_create(name="Librarian")[0]
        self.librarian_user.groups.add(group)

        self.url = reverse('main:librarian')
    
    def test_librarian_view_get_no_login(self):
        """
        If user is not authenticated, he is redirected to login page.
        """
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)
    
    def test_librarian_view_get_login_no_librarian(self):
        """
        If user is not librarian, he is redirected to login page.
        """
        self.client.login(**self.credentials)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)
    
    def test_librarian_view_get_login_librarian(self):
        """
        If user is librarian, librarian page is shown.
        """
        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/librarian.html')
    
    def test_librarian_view_get_no_books(self):
        """
        If no books exist, no books are shown.
        """
        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertQuerysetEqual(response.context['latest_book_list'], [])
    
    def test_librarian_view_get_three_books(self):
        """
        If 3 books exist, all 3 books are shown.
        """
        isbn_list = [
            '9780000000002',
            '9780000000019',
            '9780000000026'
        ]
        for isbn in isbn_list:
            Book.objects.create(isbn=isbn, name=isbn, count=1)

        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertQuerysetEqual(response.context['latest_book_list'], [
            '<Book: Book object (9780000000026)>',
            '<Book: Book object (9780000000019)>',
            '<Book: Book object (9780000000002)>'
        ])
    
    def test_librarian_view_get_six_books(self):
        """
        If 6 books exist, 5 last created books are shown.
        """
        isbn_list = [
            '9780000000002',
            '9780000000019',
            '9780000000026',
            '9780000000033',
            '9780000000040',
            '9780000000057'
        ]
        for isbn in isbn_list:
            Book.objects.create(isbn=isbn, name=isbn, count=1)

        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertQuerysetEqual(response.context['latest_book_list'], [
            '<Book: Book object (9780000000057)>',
            '<Book: Book object (9780000000040)>',
            '<Book: Book object (9780000000033)>',
            '<Book: Book object (9780000000026)>',
            '<Book: Book object (9780000000019)>'
        ])
    
    def test_librarian_view_get_no_leases(self):
        """
        If no leases exist, no leases are shown.
        """
        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertQuerysetEqual(response.context['nearest_lease_list'], [])
        
    def test_librarian_view_get_three_leases(self):
        """
        If 3 leases exist, all 3 leases are shown.
        """
        isbn_list = [
            '9780000000002',
            '9780000000019',
            '9780000000026'
        ]
        for isbn in isbn_list:
            Book.objects.create(isbn=isbn, name=isbn, count=1)
            Lease.objects.create(
                student=get_user_model().objects.get_by_natural_key(
                    self.student_credentials['username']),
                book=Book.objects.get(pk=isbn),
                expire_date=timezone.now() + timezone.timedelta(days=30))

        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.context['nearest_lease_list'].count(), 3)
        self.assertEqual(
            response.context['nearest_lease_list'][0].book.isbn,
            '9780000000002')
        self.assertEqual(
            response.context['nearest_lease_list'][2].book.isbn,
            '9780000000026')
    
    def test_librarian_view_get_six_leases(self):
        """
        If 6 leases exist, only 5 nearest leases are shown.
        """
        isbn_list = [
            '9780000000002',
            '9780000000019',
            '9780000000026',
            '9780000000033',
            '9780000000040',
            '9780000000057'
        ]
        for isbn in isbn_list:
            Book.objects.create(isbn=isbn, name=isbn, count=1)
            Lease.objects.create(
                student=get_user_model().objects.get_by_natural_key(
                    self.student_credentials['username']),
                book=Book.objects.get(pk=isbn),
                expire_date=timezone.now() + timezone.timedelta(days=30))

        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.context['nearest_lease_list'].count(), 5)
        self.assertEqual(
            response.context['nearest_lease_list'][0].book.isbn,
            '9780000000002')
        self.assertEqual(
            response.context['nearest_lease_list'][4].book.isbn,
            '9780000000040')
        
    def test_librarian_view_get_returned_leases(self):
        """
        If all leases are returned, no leases are shown.
        """
        isbn_list = [
            '9780000000002',
            '9780000000019',
            '9780000000026',
            '9780000000033',
            '9780000000040',
            '9780000000057'
        ]
        for isbn in isbn_list:
            Book.objects.create(isbn=isbn, name=isbn, count=1)
            Lease.objects.create(
                student=get_user_model().objects.get_by_natural_key(
                    self.student_credentials['username']),
                book=Book.objects.get(pk=isbn),
                expire_date=timezone.now() + timezone.timedelta(days=30),
                return_date=timezone.now())

        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertQuerysetEqual(response.context['nearest_lease_list'], [])
    
    def test_librarian_view_get_active_and_returned_leases(self):
        """
        If 3 active leases exist, only these 3 leases are shown.
        """
        isbn_list = [
            '9780000000002',
            '9780000000019',
            '9780000000026'
        ]
        another_isbn_list = [
            '9780000000033',
            '9780000000040',
            '9780000000057'
        ]
        for isbn in isbn_list:
            Book.objects.create(isbn=isbn, name=isbn, count=1)
            Lease.objects.create(
                student=get_user_model().objects.get_by_natural_key(
                    self.student_credentials['username']),
                book=Book.objects.get(pk=isbn),
                expire_date=timezone.now() + timezone.timedelta(days=30))
        for isbn in another_isbn_list:
            Book.objects.create(isbn=isbn, name=isbn, count=1)
            Lease.objects.create(
                student=get_user_model().objects.get_by_natural_key(
                    self.student_credentials['username']),
                book=Book.objects.get(pk=isbn),
                expire_date=timezone.now() + timezone.timedelta(days=30),
                return_date=timezone.now())

        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.context['nearest_lease_list'].count(), 3)
        self.assertEqual(
            response.context['nearest_lease_list'][0].book.isbn,
            '9780000000002')
        self.assertEqual(
            response.context['nearest_lease_list'][2].book.isbn,
            '9780000000026')
        
    def test_librarian_view_get_leases_ordered(self):
        """
        Leases are shown in expire date order.
        """
        isbn_list = [
            '9780000000002',
            '9780000000019',
            '9780000000026',
            '9780000000033',
            '9780000000040',
            '9780000000057'
        ]
        for i, isbn in enumerate(isbn_list):
            Book.objects.create(isbn=isbn, name=isbn, count=1)
            Lease.objects.create(
                student=get_user_model().objects.get_by_natural_key(
                    self.student_credentials['username']),
                book=Book.objects.get(pk=isbn),
                expire_date=
                    timezone.now()
                    + timezone.timedelta(days=30-i))

        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.context['nearest_lease_list'].count(), 5)
        self.assertEqual(
            response.context['nearest_lease_list'][0].book.isbn,
            '9780000000057')
        self.assertEqual(
            response.context['nearest_lease_list'][2].book.isbn,
            '9780000000033')
        self.assertEqual(
            response.context['nearest_lease_list'][4].book.isbn,
            '9780000000019')


class NewBookViewTests(TestCase):
    """
    Tests checking new book view functionality.
    """

    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'testpass'
        }
        self.user = get_user_model().objects.create_user(**self.credentials)

        self.librarian_credentials = {
            'username': 'librarian',
            'password': 'testpass'
        }
        self.librarian_user = get_user_model().objects.create_user(
            **self.librarian_credentials)
        group = Group.objects.get_or_create(name="Librarian")[0]
        self.librarian_user.groups.add(group)

        self.url = reverse('main:new_book')

    def test_new_book_view_get_no_login(self):
        """
        If user is not authenticated, he is redirected to login page.
        """
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)
    
    def test_new_book_view_get_login_no_librarian(self):
        """
        If user is not librarian, he is redirected to login page.
        """
        self.client.login(**self.credentials)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)
    
    def test_new_book_view_get_login_librarian(self):
        """
        If user is librarian, new book form is shown.
        """
        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/new_book.html')
    
    def test_new_book_view_post_adds_new_book(self):
        """
        If valid POST request is sent, new book is added.
        """
        self.client.login(**self.librarian_credentials)
        response = self.client.post(self.url, {
            'isbn': '9780000000002',
            'name': 'Test Book',
            'count': 1
        })
        self.assertRedirects(response, reverse('main:librarian'))
        self.assertEqual(
            Book.objects.get(isbn='9780000000002').name,
            'Test Book')


class BookListViewTests(TestCase):
    """
    Tests checking book list view functionality.
    """

    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'testpass'
        }
        self.user = get_user_model().objects.create_user(**self.credentials)

        self.librarian_credentials = {
            'username': 'librarian',
            'password': 'testpass'
        }
        self.librarian_user = get_user_model().objects.create_user(
            **self.librarian_credentials)
        group = Group.objects.get_or_create(name="Librarian")[0]
        self.librarian_user.groups.add(group)

        self.url = reverse('main:books')
    
    def test_book_list_view_get_no_login(self):
        """
        If user is not authenticated, he is redirected to login page.
        """
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)
    
    def test_book_list_view_get_login_no_librarian(self):
        """
        If user is not librarian, he is redirected to login page.
        """
        self.client.login(**self.credentials)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)
    
    def test_book_list_view_get_login_librarian(self):
        """
        If user is librarian, book list page is shown.
        """
        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/book_list.html')
    
    def test_book_list_view_get_no_books(self):
        """
        If no books exist, no books are shown.
        """
        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertQuerysetEqual(response.context['book_list'], [])
    
    def test_book_list_view_get_three_books(self):
        """
        If 3 books exist, all 3 books are shown.
        """
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
        """
        If 6 books exist, all 6 books are shown.
        """
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


class BookDetailViewTests(TestCase):
    """
    Tests checking book detail view functionality.
    """

    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'testpass'
        }
        self.user = get_user_model().objects.create_user(**self.credentials)

        self.librarian_credentials = {
            'username': 'librarian',
            'password': 'testpass'
        }
        self.librarian_user = get_user_model().objects.create_user(
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
        """
        If user is not authenticated, he is redirected to login page.
        """
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)
    
    def test_book_detail_view_get_login_no_librarian(self):
        """
        If user is not librarian, he is redirected to login page.
        """
        self.client.login(**self.credentials)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)
    
    def test_book_detail_view_get_login_librarian(self):
        """
        If user is librarian, book detail page is shown.
        """
        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/book_detail.html')


class NewLeaseViewTests(TestCase):
    """
    Tests checking new lease view functionality.
    """

    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'testpass'
        }
        self.user = get_user_model().objects.create_user(**self.credentials)

        self.librarian_credentials = {
            'username': 'librarian',
            'password': 'testpass'
        }
        self.librarian_user = get_user_model().objects.create_user(
            **self.librarian_credentials)
        group = Group.objects.get_or_create(name="Librarian")[0]
        self.librarian_user.groups.add(group)

        self.student_credentials = {
            'username': 'student1',
            'password': 'testpass'
        }
        self.student_user = get_user_model().objects.create_user(
            **self.student_credentials)
        group = Group.objects.get_or_create(name="Student")[0]
        self.student_user.groups.add(group)

        Book.objects.create(
            isbn='9780000000002',
            name='Test Book',
            count=1
        )

        self.url = reverse('main:new_lease', args=['9780000000002'])

    def test_new_lease_view_get_no_login(self):
        """
        If user is not authenticated, he is redirected to login page.
        """
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)

    def test_new_lease_view_get_login_no_librarian(self):
        """
        If user is not librarian, he is redirected to login page.
        """
        self.client.login(**self.credentials)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)

    def test_new_lease_view_get_login_librarian(self):
        """
        If user is librarian, new lease form is shown.
        """
        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/new_lease.html')

    def test_new_lease_view_post_adds_new_lease(self):
        """
        If valid POST request is sent, new lease is added.
        """
        self.client.login(**self.librarian_credentials)
        response = self.client.post(self.url, {
            'student': self.student_user.id,
            'book': '9780000000002',
            'expire_date': str(
                (timezone.now()+timezone.timedelta(days=30)).date())
        })
        self.assertRedirects(response, reverse('main:librarian'))
        self.assertEqual(
            Lease.objects.get(book='9780000000002').student,
            self.student_user)


class LeaseListViewTests(TestCase):
    """
    Tests checking lease list view functionality.
    """

    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'testpass'
        }
        self.user = get_user_model().objects.create_user(**self.credentials)

        self.librarian_credentials = {
            'username': 'librarian',
            'password': 'testpass'
        }
        self.librarian_user = get_user_model().objects.create_user(
            **self.librarian_credentials)
        group = Group.objects.get_or_create(name="Librarian")[0]
        self.librarian_user.groups.add(group)

        self.student_credentials = {
            'username': 'student1',
            'password': 'testpass'
        }
        self.student_user = get_user_model().objects.create_user(
            **self.student_credentials)
        group = Group.objects.get_or_create(name="Student")[0]
        self.student_user.groups.add(group)

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

        self.url = reverse('main:leases')
    
    def test_lease_list_view_get_no_login(self):
        """
        If user is not authenticated, he is redirected to login page.
        """
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)
    
    def test_lease_list_view_get_login_no_librarian(self):
        """
        If user is not librarian, he is redirected to login page.
        """
        self.client.login(**self.credentials)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)
    
    def test_lease_list_view_get_login_librarian(self):
        """
        If user is librarian, lease list page is shown.
        """
        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/lease_list.html')
    
    def test_lease_list_view_get_no_leases(self):
        """
        If no leases exist, no leases are shown.
        """
        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertQuerysetEqual(response.context['lease_list'], [])
        
    def test_lease_list_view_get_six_leases(self):
        """
        If 6 leases exist, all 6 leases are shown.
        """
        isbn_list = [
            '9780000000002',
            '9780000000019',
            '9780000000026',
            '9780000000033',
            '9780000000040',
            '9780000000057'
        ]
        for isbn in isbn_list:
            Lease.objects.create(
                student=get_user_model().objects.get_by_natural_key(
                    self.student_credentials['username']),
                book=Book.objects.get(pk=isbn),
                expire_date=timezone.now() + timezone.timedelta(days=30))

        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.context['lease_list'].count(), 6)
        self.assertEqual(
            response.context['lease_list'][0].book.isbn,
            '9780000000002')
        self.assertEqual(
            response.context['lease_list'][5].book.isbn,
            '9780000000057')
        
    def test_lease_list_view_get_leases_ordered(self):
        """
        Leases are shown in expire date order.
        """
        isbn_list = [
            '9780000000002',
            '9780000000019',
            '9780000000026',
            '9780000000033',
            '9780000000040',
            '9780000000057'
        ]
        for i, isbn in enumerate(isbn_list):
            Lease.objects.create(
                student=get_user_model().objects.get_by_natural_key(
                    self.student_credentials['username']),
                book=Book.objects.get(pk=isbn),
                expire_date=
                    timezone.now()
                    + timezone.timedelta(days=30-i))

        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.context['lease_list'].count(), 6)
        self.assertEqual(
            response.context['lease_list'][0].book.isbn,
            '9780000000057')
        self.assertEqual(
            response.context['lease_list'][3].book.isbn,
            '9780000000026')
        self.assertEqual(
            response.context['lease_list'][5].book.isbn,
            '9780000000002')


class LeaseDetailViewTests(TestCase):
    """
    Tests checking lease detail view functionality.
    """

    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'testpass'
        }
        self.user = get_user_model().objects.create_user(**self.credentials)

        self.librarian_credentials = {
            'username': 'librarian',
            'password': 'testpass'
        }
        self.librarian_user = get_user_model().objects.create_user(
            **self.librarian_credentials)
        group = Group.objects.get_or_create(name="Librarian")[0]
        self.librarian_user.groups.add(group)

        self.student_credentials = {
            'username': 'student1',
            'password': 'testpass'
        }
        self.student_user = get_user_model().objects.create_user(
            **self.student_credentials)
        group = Group.objects.get_or_create(name="Student")[0]
        self.student_user.groups.add(group)

        Book.objects.create(
            isbn='9780000000002',
            name='Test Book',
            count=1
        )

        self.lease = Lease.objects.create(
            student=get_user_model().objects.get_by_natural_key(
                self.student_credentials['username']),
            book=Book.objects.get(pk='9780000000002'),
            expire_date=timezone.now() + timezone.timedelta(days=30))

        self.url = reverse('main:lease_detail', args=[self.lease.id])

    def test_lease_detail_view_get_no_login(self):
        """
        If user is not authenticated, he is redirected to login page.
        """
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)
    
    def test_lease_detail_view_get_login_no_librarian(self):
        """
        If user is not librarian, he is redirected to login page.
        """
        self.client.login(**self.credentials)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)
    
    def test_lease_detail_view_get_login_librarian(self):
        """
        If user is librarian, lease detail page is shown.
        """
        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/lease_detail.html')


class ReturnLeaseViewTests(TestCase):
    """
    Tests checking return lease view functionality.
    """

    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'testpass'
        }
        self.user = get_user_model().objects.create_user(**self.credentials)

        self.librarian_credentials = {
            'username': 'librarian',
            'password': 'testpass'
        }
        self.librarian_user = get_user_model().objects.create_user(
            **self.librarian_credentials)
        group = Group.objects.get_or_create(name="Librarian")[0]
        self.librarian_user.groups.add(group)

        self.student_credentials = {
            'username': 'student1',
            'password': 'testpass'
        }
        self.student_user = get_user_model().objects.create_user(
            **self.student_credentials)
        group = Group.objects.get_or_create(name="Student")[0]
        self.student_user.groups.add(group)

        Book.objects.create(
            isbn='9780000000002',
            name='Test Book',
            count=1
        )

        self.lease = Lease.objects.create(
            student=get_user_model().objects.get_by_natural_key(
                self.student_credentials['username']),
            book=Book.objects.get(pk='9780000000002'),
            expire_date=timezone.now() + timezone.timedelta(days=30))

        self.url = reverse('main:return_lease', args=[self.lease.id])

    def test_return_lease_view_get_no_login(self):
        """
        If user is not authenticated, he is redirected to login page.
        """
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)

    def test_return_lease_view_get_login_no_librarian(self):
        """
        If user is not librarian, he is redirected to login page.
        """
        self.client.login(**self.credentials)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('main:login') + '?next=' + self.url)

    def test_return_lease_view_get_login_librarian(self):
        """
        If user is librarian, return lease form is shown.
        """
        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/return_lease.html')
    
    def test_return_lease_view_get_already_returned_lease(self):
        """
        If lease is already returned, user is redirected to librarian
        page.
        """
        self.lease.return_date = timezone.now()
        self.lease.save()
        self.client.login(**self.librarian_credentials)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('main:librarian'))

    def test_return_lease_view_post_returnes_lease(self):
        """
        If valid POST request is sent, lease is returned.
        """
        self.client.login(**self.librarian_credentials)
        response = self.client.post(self.url, {})
        self.assertRedirects(response, reverse('main:librarian'))
        self.assertFalse(Lease.objects.get(pk=self.lease.id).is_active())
