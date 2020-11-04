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
This module contains often used functions and data for tests in main app.
"""

from django.utils import timezone
from django.contrib.auth import get_user_model

from main.models import Book, Lease


isbn_list_6 = [
    '9780000000002',
    '9780000000019',
    '9780000000026',
    '9780000000033',
    '9780000000040',
    '9780000000057'
]

isbn_list_3_1 = [
    '9780000000002',
    '9780000000019',
    '9780000000026'
]

isbn_list_3_2 = [
    '9780000000033',
    '9780000000040',
    '9780000000057'
]


student_credentials = {
    'username': 'student1',
    'password': 'testpass'
}


def create_student_lease(isbn):
    """
    Creates lease for student.
    """
    return Lease.objects.create(
        student=get_user_model().objects.get_by_natural_key(
            student_credentials['username']),
        book=Book.objects.get(pk=isbn),
        expire_date=timezone.now() + timezone.timedelta(days=30))
