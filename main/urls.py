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
This module contains URL matches in main app.
"""

from django_registration.backends.activation import views as registration_views

from django.urls import path, include, reverse_lazy
from django.views.generic.base import RedirectView, TemplateView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.auth import views as auth_views

from . import views

app_name = 'main'

auth_urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path(
        'password_change/',
        auth_views.PasswordChangeView.as_view(
            success_url=reverse_lazy('main:password_change_done')),
        name='password_change'),
    path(
        'password_change/done/', auth_views.PasswordChangeDoneView.as_view(),
        name='password_change_done'),

    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            success_url=reverse_lazy('main:password_reset_done')),
        name='password_reset',),
    path(
        'password_reset/done/', auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done'),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            success_url=reverse_lazy('main:password_reset_complete')),
        name='password_reset_confirm'),
    path(
        'reset/done/', auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete'),
]

registration_urlpatterns = [
    path(
        "activate/complete/",
        TemplateView.as_view(
            template_name="django_registration/activation_complete.html"
        ),
        name="activation_complete",
    ),
    path(
        "activate/<str:activation_key>/",
        registration_views.ActivationView.as_view(
            success_url=reverse_lazy(
                'main:activation_complete')
        ),
        name="activate",
    ),
    path(
        "register/",
        views.RegisterView.as_view(),
        name="register",
    ),
    path(
        "register/complete/",
        TemplateView.as_view(
            template_name="django_registration/registration_complete.html"
        ),
        name="registration_complete",
    ),
    path(
        "register/closed/",
        TemplateView.as_view(
            template_name="django_registration/registration_closed.html"
        ),
        name="registration_disallowed",
    ),
]

urlpatterns = [
    path('', views.index, name='index'),
    path('', include(auth_urlpatterns)),
    path('', include(registration_urlpatterns)),
    path(
        'favicon.ico',
        RedirectView.as_view(url=staticfiles_storage.url('main/favicon.ico'))),
    path('profile/', views.profile, name='profile'),
    path('admin/', views.admin, name='admin'),
    path(
        'admin/select_theme/',
        views.SelectThemeView.as_view(),
        name='select_theme'),
    path(
        'admin/register_librarian/',
        views.LibrarianRegisterView.as_view(),
        name='register_librarian'),
    path(
        "activate_librarian/<str:activation_key>/",
        views.LibrarianActivationView.as_view(),
        name="activate_librarian",
    ),
    path('student/', views.student, name='student'),
    path('librarian/', views.librarian, name='librarian'),
    path('librarian/books/', views.BookListView.as_view(), name='books'),
    path('librarian/new_book/', views.new_book, name='new_book'),
    path(
        'librarian/books/<slug:pk>/', views.BookDetailView.as_view(),
        name='book_detail'),
    path(
        'librarian/books/<slug:book_id>/edit/', views.edit_book,
        name='edit_book'),
    path(
        'librarian/books/<slug:book_id>/new_lease/', views.new_lease,
        name='new_lease'),
    path('librarian/leases/', views.LeaseListView.as_view(), name='leases'),
    path(
        'librarian/leases/<slug:pk>/', views.LeaseDetailView.as_view(),
        name='lease_detail'),
    path(
        'librarian/leases/<slug:lease_id>/return/', views.return_lease,
        name='return_lease'),
    path('librarian/xlsx_report/', views.xlsx_report, name='xlsx_report')
]
