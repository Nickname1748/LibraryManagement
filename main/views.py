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
This module contains all views in main app.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.views import generic
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError

from .decorators import group_required
from .models import Book, Lease
from .forms import BookCreationForm, LeaseCreationForm
from .utils import build_xlsx


@login_required
def index(request):
    """
    Default page that redirects users to role specific pages.
    """
    if request.user.is_staff:
        return redirect('main:admin')
    if request.user.groups.filter(name='Librarian').exists():
        return redirect('main:librarian')
    return redirect('main:student')



def register(request):
    """
    Register page allows registeration of new users.
    """
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


@staff_member_required
def admin(request):
    """
    Admin panel.
    """
    logs = LogEntry.objects.all()
    context = {'logs': logs}
    return render(request, 'main/admin.html', context=context)


@group_required('Student')
def student(request):
    """
    Main page of student UI.
    """
    active_lease_list = Lease.objects\
        .filter(student__username__exact=request.user.username)\
        .filter(return_date__isnull=True).order_by('expire_date')
    context = {
        'active_lease_list': active_lease_list
    }
    return render(request, 'main/student.html', context=context)


@group_required('Librarian')
def librarian(request):
    """
    Main page of librarian UI.
    """
    nearest_lease_list = Lease.objects.filter(return_date__isnull=True)\
        .order_by('expire_date')[:5]
    latest_book_list = \
        Book.objects.filter(count__gt=0).order_by('-added_date')[:5]
    context = {
        'latest_book_list': latest_book_list,
        'nearest_lease_list': nearest_lease_list
    }

    return render(request, 'main/librarian.html', context=context)


@group_required('Librarian')
def new_book(request):
    """
    Page that allows librarian to add new book.
    """
    if request.method == 'POST':
        form = BookCreationForm(request.POST)
        if form.is_valid():
            form.save()
            LogEntry.objects.log_action(
                request.user.id,
                ContentType.objects.get(app_label='main', model='book').id,
                form.instance.isbn,
                repr(form.instance),
                action_flag=ADDITION,
                change_message="New book")
            return redirect('main:librarian')
    else:
        form = BookCreationForm()

    return render(request, 'main/new_book.html', {'form': form})


@method_decorator(group_required('Librarian'), name='dispatch')
class BookListView(generic.ListView):
    """
    Page that lists all books.
    """
    model = Book
    paginate_by = 25

    def get_queryset(self):
        try:
            query = self.request.GET['q']
        except MultiValueDictKeyError:
            query = ''

        if query != '':
            return self.model.objects.filter(name__icontains=query)\
                .order_by('-added_date')

        return self.model.objects.order_by('-added_date')


@method_decorator(group_required('Librarian'), name='dispatch')
class BookDetailView(generic.DetailView):
    """
    Page that shows details of book.
    """
    model = Book


@group_required('Librarian')
def edit_book(request, book_id):
    """
    Page that allows librarian to edit book.
    """
    book = get_object_or_404(Book, pk=book_id)
    if request.method == 'POST':
        form = BookCreationForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            LogEntry.objects.log_action(
                request.user.id,
                ContentType.objects.get(app_label='main', model='book').id,
                form.instance.isbn,
                repr(form.instance),
                action_flag=CHANGE,
                change_message="Book edited")
            return redirect('main:librarian')
    else:
        form = BookCreationForm(instance=book)

    return render(request, 'main/edit_book.html', {
        'form': form,
        'book_id': book_id
    })


@group_required('Librarian')
def new_lease(request, book_id):
    """
    Page that allows to lease a book.
    """
    book = get_object_or_404(Book, pk=book_id)
    if request.method == 'POST':
        form = LeaseCreationForm(request.POST)
        if form.is_valid():
            form.save()
            LogEntry.objects.log_action(
                request.user.id,
                ContentType.objects.get(app_label='main', model='lease').id,
                form.instance.id,
                repr(form.instance),
                action_flag=ADDITION,
                change_message="New lease")
            return redirect('main:librarian')
    else:
        form = LeaseCreationForm(initial={'book': book_id})

    return render(request, 'main/new_lease.html', {
        'form': form,
        'book_id': book_id,
        'book_name': book.name
    })


@method_decorator(group_required('Librarian'), name='dispatch')
class LeaseListView(generic.ListView):
    """
    Page that shows list of active leases.
    """
    model = Lease
    paginate_by = 25

    def get_queryset(self):
        try:
            query = self.request.GET['q']
        except MultiValueDictKeyError:
            query = ''

        if query != '':
            return self.model.objects\
                .filter(student__username__icontains=query)\
                .order_by('expire_date')

        return self.model.objects.order_by('expire_date')


@method_decorator(group_required('Librarian'), name='dispatch')
class LeaseDetailView(generic.DetailView):
    """
    Page that shows lease details.
    """
    model = Lease


@group_required('Librarian')
def return_lease(request, lease_id):
    """
    Page that allows to return leased book.
    """
    lease = get_object_or_404(Lease, pk=lease_id)
    if not lease.is_active():
        return redirect('main:librarian')
    if request.method == 'POST':
        lease.return_date = timezone.now()
        lease.save()
        LogEntry.objects.log_action(
            request.user.id,
            ContentType.objects.get(app_label='main', model='lease').id,
            lease_id,
            repr(lease),
            action_flag=CHANGE,
            change_message="Lease returned")
        return redirect('main:librarian')

    return render(request, 'main/return_lease.html', {
        'lease': lease
    })


@group_required('Librarian')
def xlsx_report(request):
    """
    Returnes XLSX report file for download.
    """
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename = "Report.xlsx"'

    workbook = build_xlsx()
    workbook.save(response)

    return response
