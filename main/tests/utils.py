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

from django.conf import settings
from django.core import signing
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from main.models import Book, Lease


REGISTRATION_SALT = getattr(settings, "REGISTRATION_SALT", "registration")


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


test_credentials = {
    'username': 'testuser',
    'password': 'testpass'
}


admin_credentials = {
    'username': 'admin',
    'password': 'testpass'
}


librarian_credentials = {
    'username': 'librarian',
    'password': 'testpass'
}


student_credentials = {
    'username': 'student1',
    'password': 'testpass'
}


def create_test_user():
    """
    Creates test user.
    """
    admin = get_user_model().objects.create_user(
        **test_credentials,
        email='test@example.com',
        first_name='Name',
        last_name='Surname'
    )
    return admin


def create_admin_user():
    """
    Creates admin user.
    """
    admin = get_user_model().objects.create_user(
        **admin_credentials,
        email='admin@example.com',
        first_name='AdminName',
        last_name='AdminSurname'
    )
    admin.is_staff = True
    admin.save()
    return admin


def create_librarian_user():
    """
    Creates librarian user.
    """
    librarian = get_user_model().objects.create_user(
        **librarian_credentials,
        email='librarian@example.com',
        first_name='LibrarianName',
        last_name='LibrarianSurname'
    )
    group = Group.objects.get_or_create(name="Librarian")[0]
    librarian.groups.add(group)
    return librarian


def create_inactive_librarian_user():
    """
    Creates librarian user.
    """
    librarian = get_user_model().objects.create_user(
        **librarian_credentials,
        email='librarian@example.com',
        first_name='LibrarianName',
        last_name='LibrarianSurname',
        is_active=False
    )
    group = Group.objects.get_or_create(name="Librarian")[0]
    librarian.groups.add(group)
    return librarian


def create_student_user():
    """
    Creates student user.
    """
    student = get_user_model().objects.create_user(
        **student_credentials,
        email='student@example.com',
        first_name='StudentName',
        last_name='StudentSurname'
    )
    group = Group.objects.get_or_create(name="Student")[0]
    student.groups.add(group)
    return student


def get_user(username):
    """
    Returnes user by username.
    """
    return get_user_model().objects.get(username=username)


def check_user_in_group(username, group):
    """
    Checks if user is a member of group.
    """
    return (
        Group.objects.get(name=group)
        in get_user(username).groups.all())


def check_user_is_active(username):
    """
    Checks if user is active
    """
    return get_user(username).is_active


def generate_activation_key(user):
    """
    Generates activation key for user.
    """
    return signing.dumps(obj=user.get_username(), salt=REGISTRATION_SALT)


def create_student_lease(isbn):
    """
    Creates lease for student.
    """
    return Lease.objects.create(
        student=get_user_model().objects.get_by_natural_key(
            student_credentials['username']),
        book=Book.objects.get(pk=isbn),
        expire_date=timezone.now() + timezone.timedelta(days=30))
