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

from django.contrib.auth.models import User

class Book(models.Model):
    isbn = models.PositiveBigIntegerField()
    name = models.CharField(max_length=255)
    count = models.IntegerField()
    available_count = models.IntegerField()
    status = models.IntegerField()

class Lease(models.Model):
    customer = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    librarian = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    issue_date = models.DateTimeField()
    return_date = models.DateTimeField()
    status = models.IntegerField()
