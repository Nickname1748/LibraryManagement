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

from django.urls import path, include

from . import views

app_name = 'main'
urlpatterns = [
    path('', views.index, name='index'),
    path('', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('librarian/', views.librarian, name='librarian'),
    path('librarian/books/', views.BookListView.as_view(), name='books'),
    path('librarian/new_book/', views.new_book, name='new_book'),
    path('librarian/books/<slug:pk>/', views.BookDetailView.as_view(),
         name='book_detail'),
    path('librarian/books/<slug:book_id>/new_lease/', views.new_lease,
         name='new_lease'),
     path('librarian/leases/<slug:pk>/', views.LeaseDetailView.as_view(),
         name='lease_detail')
]
