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

from django.forms import ModelForm, ValidationError, HiddenInput
import stdnum.isbn

from .models import Book, Lease


class BookCreationForm(ModelForm):
    class Meta:
        model = Book
        exclude = ['added_date']
        widgets = {
            'book': HiddenInput()
        }
    
    def clean_isbn(self):
        return stdnum.isbn.to_isbn13(self.cleaned_data['isbn'])
    
    def clean_count(self):
        if self.cleaned_data['count'] == 0:
            raise ValidationError('Invalid value')
        return self.cleaned_data['count']

class LeaseCreationForm(ModelForm):
    class Meta:
        model = Lease
        exclude = ['issue_date', 'return_date']
