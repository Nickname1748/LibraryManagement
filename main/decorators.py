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
This module contains custom decorators used in main app.
"""

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.admin.views.decorators import staff_member_required


def admin_required(view_func=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user is staff, redirecting
    to the login page if necessary.
    """
    return staff_member_required(
        view_func=view_func,
        redirect_field_name=redirect_field_name,
        login_url='main:login')


def group_required(*group_names):
    """
    Decorator for views that checks that the user is a member of given
    group, redirecting to the login page if necessary.
    """

    def in_group(user):
        return user.is_active and (
            user.is_superuser
            or bool(user.groups.filter(name__in=group_names)))

    return user_passes_test(in_group)
