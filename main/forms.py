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

import stdnum.isbn
from django_registration.forms import RegistrationForm

from django import forms
from django.utils import timezone
from django.utils.translation import gettext as _, ngettext
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model


from .models import Book, Lease


class RegisterForm(RegistrationForm):
    """
    The form used for user registration.
    """
    first_name = forms.CharField(max_length=30, label=_("First name"))
    last_name = forms.CharField(max_length=30,  label=_("Last name"))
    email = forms.EmailField(label=_("Email"))

    class Meta:
        model = get_user_model()
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2'
        ]


class LibrarianRegisterForm(RegistrationForm):
    """
    The form used for librarian registration.
    """
    first_name = forms.CharField(max_length=30, label=_("First name"))
    last_name = forms.CharField(max_length=30,  label=_("Last name"))
    email = forms.EmailField(label=_("Email"))

    class Meta:
        model = get_user_model()
        fields = [
            'username',
            'first_name',
            'last_name',
            'email'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.HiddenInput()
        self.fields['password2'].widget = forms.HiddenInput()
        self.fields['password1'].required = False
        self.fields['password2'].required = False


class EditProfileForm(forms.ModelForm):
    """
    The form used to edit profile.
    """

    class Meta:
        model = get_user_model()
        fields = [
            'username',
            'first_name',
            'last_name',
            'email'
        ]


THEMES = (
    ('default', _("Light (Default)")),
    ('dark', _("Dark"))
)


class ThemeSelectionForm(forms.Form):
    """
    The form which allows to select visual theme.
    """
    theme = forms.ChoiceField(choices=THEMES)


class BookCreationForm(forms.ModelForm):
    """
    The form which allows to create new Book instance.
    """
    count = forms.IntegerField(
        validators=[MinValueValidator(0)], min_value=0, label=_("Count"))

    class Meta:
        model = Book
        fields = ['isbn', 'name', 'authors', 'count']

    def clean_isbn(self):
        """
        ISBN passed to model must be in ISBN-13 format.
        """
        return stdnum.isbn.to_isbn13(self.cleaned_data['isbn'])

    def clean_count(self):
        """
        If book exists, count must be not less than leased book count.
        """
        count = self.cleaned_data['count']
        try:
            book_isbn = self.cleaned_data['isbn']
        except KeyError:
            raise forms.ValidationError(_('No ISBN is sent')) from None
        if Book.objects.filter(pk=book_isbn).exists():
            book = Book.objects.get(pk=book_isbn)
            lease_count = book.lease_set.filter(return_date__isnull=True)\
                .count()
            if count < lease_count:
                raise forms.ValidationError(
                    (ngettext(
                        '{0} book is leased, '
                        'so minimum allowed book count is {0}',
                        '{0} books are leased, '
                        'so minimum allowed book count is {0}',
                        lease_count))
                    .format(lease_count))
        return count


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
            raise forms.ValidationError(_('Book is not available for leasing'))
        return book

    def clean_expire_date(self):
        """
        Expire date must be in future.
        """
        expire_date = self.cleaned_data['expire_date']
        if expire_date <= timezone.now().date():
            raise forms.ValidationError(_('Expire date must be in future'))
        return expire_date
