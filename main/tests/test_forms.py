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

from main.forms import BookCreationForm


class BookCreationFormTests(TestCase):

    def test_book_creation_form_valid_data_13(self):
        form = BookCreationForm(data={
            'isbn': '9780000000002',
            'name': 'Test Book',
            'count': 1
        })
        self.assertTrue(form.is_valid())
    
    def test_book_creation_form_valid_data_10(self):
        form = BookCreationForm(data={
            'isbn': '0000000000',
            'name': 'Test Book',
            'count': 1
        })
        self.assertTrue(form.is_valid())
        self.assertEquals(form.cleaned_data['isbn'], '9780000000002')
    
    def test_book_creation_form_no_data(self):
        form = BookCreationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3)
    
    def test_book_creation_form_no_isbn(self):
        form = BookCreationForm(data={
            'name': 'Test Book',
            'count': 1
        })
        self.assertFalse(form.is_valid())

    def test_book_creation_form_invalid_isbn(self):
        form = BookCreationForm(data={
            'isbn': '9780000000001',
            'name': 'Test Book',
            'count': 1
        })
        self.assertFalse(form.is_valid())
    
    def test_book_creation_form_no_name(self):
        form = BookCreationForm(data={
            'isbn': '9780000000002',
            'count': 1
        })
        self.assertFalse(form.is_valid())
    
    def test_book_creation_form_no_count(self):
        form = BookCreationForm(data={
            'isbn': '9780000000002',
            'name': 'Test Book'
        })
        self.assertFalse(form.is_valid())
    
    def test_book_creation_form_count_is_zero(self):
        form = BookCreationForm(data={
            'isbn': '9780000000002',
            'name': 'Test Book',
            'count': 0
        })
        self.assertFalse(form.is_valid())
