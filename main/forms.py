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

from django import forms
from django.core.validators import MinValueValidator
from django.utils import timezone

import stdnum.isbn

from .models import Book, Lease


class BookCreationForm(forms.ModelForm):
    count = forms.IntegerField(validators=[MinValueValidator(1)], min_value=1)
    
    class Meta:
        model = Book
        exclude = ['added_date']
    
    def clean_isbn(self):
        return stdnum.isbn.to_isbn13(self.cleaned_data['isbn'])

class LeaseCreationForm(forms.ModelForm):

    class Meta:
        model = Lease
        exclude = ['issue_date', 'return_date']

    def clean_book(self):
        book = self.cleaned_data['book']
        if book.available_count() <= 0:
            raise forms.ValidationError('Book is not available')
        return book
