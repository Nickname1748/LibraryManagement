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
This module contains all forms of main app.
"""

from django import forms
from django.core.validators import MinValueValidator

import stdnum.isbn

from .models import Book, Lease


class BookCreationForm(forms.ModelForm):
    """
    The form which allows to create new Book instance.
    """
    count = forms.IntegerField(validators=[MinValueValidator(1)], min_value=1)

    class Meta:
        model = Book
        fields = ['isbn', 'name', 'count']

    def clean_isbn(self):
        """
        ISBN passed to model must be in ISBN-13 format.
        """
        return stdnum.isbn.to_isbn13(self.cleaned_data['isbn'])


class LeaseCreationForm(forms.ModelForm):
    """
    The form which allows to create new Lease instance.
    """

    class Meta:
        model = Lease
        fields = ['student', 'book', 'expire_date']

    def clean_book(self):
        """
        Book must be available to be leased.
        """
        book = self.cleaned_data['book']
        if book.available_count() <= 0:
            raise forms.ValidationError('Book is not available')
        return book
