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

from django.db import models
from django.utils import timezone
from isbn_field import ISBNField

from django.contrib.auth.models import User

class Book(models.Model):
    isbn = ISBNField(primary_key=True)
    name = models.CharField(max_length=255)
    added_date = models.DateTimeField(default=timezone.now)
    count = models.IntegerField()
    available_count = models.IntegerField()

class Lease(models.Model):
    ACTIVE = 0
    EXPIRED = 1
    RETURNED = 2
    STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (EXPIRED, 'Expired'),
        (RETURNED, 'Returned'),
    )

    customer = models.ForeignKey(User, on_delete=models.PROTECT)
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    issue_date = models.DateTimeField()
    expire_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
