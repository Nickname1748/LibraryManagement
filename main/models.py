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

import uuid
from django.db import models
from django.utils import timezone
from isbn_field import ISBNField
from django.contrib.auth.models import User


class Book(models.Model):
    isbn = ISBNField(primary_key=True)
    name = models.CharField(max_length=255)
    added_date = models.DateTimeField(auto_now_add=True)
    count = models.PositiveSmallIntegerField()

    def is_active(self):
        return self.count > 0
    
    def available_count(self):
        return max(self.count - self.lease_set.count(), 0)

    def is_available(self):
        return self.count > 0 and self.available_count() > 0


class Lease(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(User, on_delete=models.PROTECT)
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    issue_date = models.DateTimeField(auto_now_add=True)
    expire_date = models.DateField()
    return_date = models.DateTimeField(null=True)

    def is_active(self):
        return not bool(self.return_date)
