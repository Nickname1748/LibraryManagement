""" Library Management System
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
from isbn_field import ISBNField

class BookCreationForm(forms.Form):
    isbn = forms.IntegerField(label="ISBN (13 или 10 цифр)")
    name = forms.CharField(max_length=255, label="Название книги")
    count = forms.IntegerField(label="Общее количество книг")
    available_count = forms.IntegerField(label="Доступное количество книг")