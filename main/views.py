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

from django.shortcuts import render, redirect
from django.http import HttpResponse, request
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.views import generic

from .decorators import group_required
from .models import Book, Lease
from .forms import BookCreationForm, LeaseCreationForm


@login_required
def index(request):
    return HttpResponse(
        "Welcome to Library Management System! Your name is %s"
        % request.user.username)


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = request.POST['username']
            password = request.POST['password1']
            user = authenticate(request, username=username, password=password)
            group = Group.objects.get_or_create(name="Student")[0]
            user.groups.add(group)
            login(request, user)

            return redirect('main:index')
    else:
        form = UserCreationForm()

    context = {'form': form}
    return render(request, 'registration/register.html', context=context)


@group_required('Librarian')
def librarian(request):
    nearest_lease_list = Lease.objects.order_by('expire_date')[:5]
    latest_book_list = \
        Book.objects.filter(count__gt=0).order_by('-added_date')[:5]
    context = {
        'latest_book_list': latest_book_list,
        'nearest_lease_list': nearest_lease_list
    }

    return render(request, 'main/librarian.html', context=context)


@group_required('Librarian')
def new_book(request):
    if request.method == 'POST':
        form = BookCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('main:librarian')
    else:
        form = BookCreationForm()

    return render(request, 'main/new_book.html', {'form': form})


@method_decorator(group_required('Librarian'), name='dispatch')
class BookListView(generic.ListView):
    model = Book
    paginate_by = 25

    def get_queryset(self):
        try:
            query = self.request.GET['q']
        except:
            query = ''

        if query != '':
            return self.model.objects.filter(name__icontains=query)\
                .order_by('-added_date')

        return self.model.objects.order_by('-added_date')


@method_decorator(group_required('Librarian'), name='dispatch')
class BookDetailView(generic.DetailView):
    model = Book


@group_required('Librarian')
def new_lease(request, book_id):
    if request.method == 'POST':
        form = LeaseCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('main:librarian')
    else:
        form = LeaseCreationForm(initial={'book': book_id})

    return render(request, 'main/new_lease.html', {
        'form': form,
        'book_id': book_id
    })
