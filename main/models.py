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
This module contains models in main app.
"""

import uuid
from isbn_field import ISBNField
from stdnum import isbn

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom user model for main app.
    """
    email = models.EmailField(unique=True, verbose_name=gettext_lazy("Email"))

    def __str__(self):
        return "{} {} [{}]".format(
            self.first_name, self.last_name, self.username)

    def role(self):
        """
        Returns role of user.
        """
        if self.is_staff:
            return gettext_lazy("Administrator")
        if self.groups.filter(name='Librarian').exists():
            return gettext_lazy("Librarian")
        return gettext_lazy("Student")


class Book(models.Model):
    """
    Book model describes book object in main app.
    """
    isbn = ISBNField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name=gettext_lazy("Name"))
    authors = models.CharField(
        max_length=255, verbose_name=gettext_lazy("Authors"))
    added_date = models.DateTimeField(
        auto_now_add=True, verbose_name=gettext_lazy("Added date"))
    count = models.PositiveSmallIntegerField(
        verbose_name=gettext_lazy("Count"))

    def __str__(self):
        return "{} [{}]".format(self.name, self.authors)

    def formatted_isbn(self):
        """
        Returns ISBN in proper format woth dashes.
        """
        return isbn.format(self.isbn)

    def truncated_name(self):
        """
        Returns shortened name for displaying in lists and cards.
        """
        if len(self.name) <= 100:
            return self.name

        short_name = self.name[:100]
        words = short_name.split(' ')[:-1]

        return ' '.join(words) + '…'

    def is_active(self):
        """
        Returns True if count is greater than 0. Otherwise returns
        False.
        """
        return self.count > 0

    def available_count(self):
        """
        Returns count - leased books count.
        """
        return max(
            self.count
            - self.lease_set.filter(return_date__isnull=True).count(),
            0)

    def is_available(self):
        """
        Returns True if self.available_count() is greater than 0.
        Otherwise returns False.
        """
        return self.count > 0 and self.available_count() > 0


class Lease(models.Model):
    """
    Lease model describes book lease object in main app.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=gettext_lazy("ID"))
    student = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        verbose_name=gettext_lazy("Student"))
    book = models.ForeignKey(
        Book, on_delete=models.PROTECT, verbose_name=gettext_lazy("Book"))
    issue_date = models.DateTimeField(
        auto_now_add=True, verbose_name=gettext_lazy("Issue date"))
    expire_date = models.DateField(verbose_name=gettext_lazy("Expire date"))
    return_date = models.DateTimeField(
        null=True, verbose_name=gettext_lazy("Return date"))

    def is_active(self):
        """
        Returns True if book is not returned (self.return_date is Null).
        Otherwise returns False.
        """
        return not bool(self.return_date)

    def is_expired(self):
        """
        Returns True if active and expire date is in the past. Otherwise
        returns False.
        """
        if not self.is_active():
            return False
        today = timezone.now().date()
        if self.expire_date < today:
            return True
        return False

    def is_expiring(self):
        """
        Returns True if active and expire date is today. Otherwise
        returns False.
        """
        if not self.is_active():
            return False
        soon = (timezone.now() + timezone.timedelta(days=2)).date()
        if self.expire_date < soon:
            return True
        return False

    def status(self):
        """
        Returns lease status in human format.
        """
        if not self.is_active():
            return gettext_lazy("Returned")
        if self.is_expired():
            return gettext_lazy("Expired")
        if self.is_expiring():
            return gettext_lazy("Expiring")
        return gettext_lazy("Active")
