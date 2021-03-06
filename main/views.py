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

import os

from django_registration.backends.activation.views import (
    RegistrationView, ActivationView)

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model, login
from django.views import generic
from django.utils import timezone
from django.utils.translation import gettext_lazy
from django.urls import reverse_lazy
from django.conf import settings
from django.db.models import Q

from .decorators import admin_required, group_required
from .models import Book, Lease
from .forms import (
    BookUpdateForm, RegisterForm, LibrarianRegisterForm, EditProfileForm,
    ThemeSelectionForm, BookCreationForm, LeaseCreationForm)
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


class RegisterView(RegistrationView):
    """
    Register page allows registration of new users.
    """

    form_class = RegisterForm
    success_url = reverse_lazy('main:registration_complete')
    disallowed_url = reverse_lazy('main:registration_disallowed')

    def create_inactive_user(self, form):
        new_user = super().create_inactive_user(form)
        group = Group.objects.get_or_create(name="Student")[0]
        new_user.groups.add(group)
        new_user.save()

        return new_user


@method_decorator(admin_required, name='dispatch')
class LibrarianRegisterView(RegistrationView):
    """
    Register page allows registration of new librarians.
    """

    form_class = LibrarianRegisterForm
    success_url = reverse_lazy('main:admin')
    disallowed_url = reverse_lazy('main:registration_disallowed')
    template_name = 'main/librarian_registration.html'
    email_body_template = "main/librarian_email_body.txt"

    def __init__(self):
        super().__init__()
        self.password = get_user_model().objects.make_random_password()

    def create_inactive_user(self, form):
        new_user = form.save(commit=False)
        new_user.is_active = False
        new_user.set_password(self.password)
        new_user.save()
        group = Group.objects.get_or_create(name="Librarian")[0]
        new_user.groups.add(group)
        new_user.save()
        LogEntry.objects.log_action(
            self.request.user.id,
            ContentType.objects.get(app_label='main', model='user').id,
            new_user.id,
            repr(new_user),
            action_flag=ADDITION,
            change_message=gettext_lazy("New librarian added"))

        self.send_activation_email(new_user)

        return new_user

    def get_email_context(self, activation_key):
        context = super().get_email_context(activation_key)
        context['password'] = self.password
        return context


class LibrarianActivationView(ActivationView):
    """
    Activates librarian user and redirects to password change view.
    """

    success_url = reverse_lazy('main:password_change')

    def activate(self, *args, **kwargs):
        user = super().activate(*args, **kwargs)
        login(self.request, user)
        return user


@login_required
def profile(request):
    """
    User profile page.
    """
    return render(request, 'main/profile.html')


@login_required
def edit_profile(request):
    """
    Edit profile page.
    """
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('main:profile')
    else:
        form = EditProfileForm(instance=request.user)

    context = {
        'form': form
    }
    return render(request, 'main/edit_profile.html', context=context)


@admin_required
def admin(request):
    """
    Admin panel.
    """
    logs = LogEntry.objects.all().order_by('-action_time')[:15]
    context = {'logs': logs}
    return render(request, 'main/admin.html', context=context)


@method_decorator(admin_required, name='dispatch')
class LogListView(generic.ListView):
    """
    Log list view.
    """
    model = LogEntry
    paginate_by = 15
    template_name = 'main/logentry_list.html'

    def get_queryset(self):
        return self.model.objects.order_by('-action_time')


@method_decorator(admin_required, name='dispatch')
class UserListView(generic.ListView):
    """
    User list view.
    """
    model = get_user_model()
    paginate_by = 10

    def get_queryset(self):
        return self.model.objects.order_by('-last_login')


@method_decorator(admin_required, name='dispatch')
class AdminProfileView(generic.DetailView):
    """
    Profile view for admins.
    """
    model = get_user_model()
    template_name = 'main/admin_profile.html'

    def get_context_data(self, **kwargs):
        context = {}
        if self.object:
            context['object'] = self.object
        context.update(kwargs)
        return context


@admin_required
def block_user(request, user_id):
    """
    Page that allows to block user.
    """
    user = get_object_or_404(get_user_model(), pk=user_id)
    if user == request.user:
        return redirect('main:admin_profile', pk=user_id)
    if not user.is_active:
        return redirect('main:admin_profile', pk=user_id)
    if request.method == 'POST':
        user.is_active = False
        user.save()
        LogEntry.objects.log_action(
            request.user.id,
            ContentType.objects.get(app_label='main', model='user').id,
            user.id,
            repr(user),
            action_flag=CHANGE,
            change_message=gettext_lazy("User blocked"))
        return redirect('main:admin_profile', pk=user_id)

    return render(request, 'main/block_user.html', {
        'object': user
    })


@admin_required
def unblock_user(request, user_id):
    """
    Page that allows to unblock user.
    """
    user = get_object_or_404(get_user_model(), pk=user_id)
    if user.is_active:
        return redirect('main:admin_profile', pk=user_id)
    if request.method == 'POST':
        user.is_active = True
        user.save()
        LogEntry.objects.log_action(
            request.user.id,
            ContentType.objects.get(app_label='main', model='user').id,
            user.id,
            repr(user),
            action_flag=CHANGE,
            change_message=gettext_lazy("User unblocked"))
        return redirect('main:admin_profile', pk=user_id)

    return render(request, 'main/unblock_user.html', {
        'object': user
    })


@method_decorator(admin_required, name='dispatch')
class SelectThemeView(generic.edit.FormView):
    """
    Page that allows to change theme.
    """
    template_name = 'main/select_theme.html'
    form_class = ThemeSelectionForm
    success_url = reverse_lazy('main:admin')

    def form_valid(self, form):
        base_dir = str(getattr(settings, 'BASE_DIR'))
        theme_file = (
            form.cleaned_data['theme']
            + '.css')
        active_path = base_dir + '/main/static/main/css/active.css'
        if os.path.exists(active_path):
            os.remove(active_path)
        os.symlink(theme_file, active_path)
        return super().form_valid(form)


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


@method_decorator(group_required('Student'), name='dispatch')
class LeaseHistoryView(generic.ListView):
    """
    Page that shows lease history.
    """
    model = Lease
    paginate_by = 10
    template_name = 'main/lease_list_student.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'q': self.request.GET.get('q', ''),
            'active': self.request.GET.get('active', 'all')
        })
        return context

    def get_queryset(self):
        query = self.request.GET.get('q', '')

        queryset = (
            self.model.objects
            .filter(student__username__exact=self.request.user.username))

        if query != '':
            queryset = queryset.filter(
                Q(book__name__icontains=query)
                | Q(book__authors__icontains=query))

        active = self.request.GET.get('active', 'all')

        if active == 'yes':
            queryset = queryset.filter(return_date__isnull=True)
        elif active == 'no':
            queryset = queryset.filter(return_date__isnull=False)

        queryset = queryset.order_by('return_date', 'expire_date')

        return queryset


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


@method_decorator(group_required('Librarian'), name='dispatch')
class BookCreateView(generic.edit.CreateView):
    """
    Page that allows librarian to add new book.
    """
    template_name = 'main/new_book.html'
    form_class = BookCreationForm

    def form_valid(self, form):
        form.save()
        LogEntry.objects.log_action(
            self.request.user.id,
            ContentType.objects.get(app_label='main', model='book').id,
            form.instance.isbn,
            repr(form.instance),
            action_flag=ADDITION,
            change_message=gettext_lazy("New book"))
        return redirect('main:book_detail', pk=form.instance.isbn)


@method_decorator(group_required('Librarian'), name='dispatch')
class BookListView(generic.ListView):
    """
    Page that lists all books.
    """
    model = Book
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'q': self.request.GET.get('q', '')
        })
        return context

    def get_queryset(self):
        query = self.request.GET.get('q', '')

        queryset = self.model.objects.all()

        if query != '':
            queryset = queryset.filter(
                Q(name__icontains=query)
                | Q(authors__icontains=query))

        queryset = queryset.order_by('-added_date')

        return queryset


@method_decorator(group_required('Librarian'), name='dispatch')
class BookDetailView(generic.DetailView):
    """
    Page that shows details of book.
    """
    model = Book


@method_decorator(group_required('Librarian'), name='dispatch')
class BookEditView(generic.edit.UpdateView):
    """
    Page that allows librarian to edit book.
    """
    template_name = 'main/edit_book.html'
    form_class = BookUpdateForm
    model = Book

    def form_valid(self, form):
        form.save()
        LogEntry.objects.log_action(
            self.request.user.id,
            ContentType.objects.get(app_label='main', model='book').id,
            form.instance.isbn,
            repr(form.instance),
            action_flag=CHANGE,
            change_message=gettext_lazy("Book edited"))
        return redirect('main:book_detail', pk=form.instance.isbn)


@method_decorator(group_required('Librarian'), name='dispatch')
class LeaseCreateView(generic.edit.CreateView):
    """
    Page that allows to lease a book.
    """
    template_name = 'main/new_lease.html'
    form_class = LeaseCreationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'book_name': Book.objects.get(pk=self.kwargs['book_id']).name
        })
        return context

    def get_initial(self, **kwargs):
        initial = super().get_initial(**kwargs)
        initial.update({
            'book': self.kwargs['book_id']
            })
        return initial

    def form_valid(self, form):
        form.save()
        LogEntry.objects.log_action(
            self.request.user.id,
            ContentType.objects.get(app_label='main', model='lease').id,
            form.instance.id,
            repr(form.instance),
            action_flag=ADDITION,
            change_message=gettext_lazy("New lease"))
        return redirect('main:lease_detail', pk=form.instance.id)


@method_decorator(group_required('Librarian'), name='dispatch')
class LeaseListView(generic.ListView):
    """
    Page that shows list of active leases.
    """
    model = Lease
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'q': self.request.GET.get('q', ''),
            'active': self.request.GET.get('active', 'all')
        })
        return context

    def get_queryset(self):
        query = self.request.GET.get('q', '')

        queryset = self.model.objects.all()

        if query != '':
            queryset = queryset.filter(
                Q(student__username__icontains=query)
                | Q(student__first_name__icontains=query)
                | Q(student__last_name__icontains=query)
                | Q(book__name__icontains=query)
                | Q(book__authors__icontains=query))

        active = self.request.GET.get('active', 'all')

        if active == 'yes':
            queryset = queryset.filter(return_date__isnull=True)
        elif active == 'no':
            queryset = queryset.filter(return_date__isnull=False)

        queryset = queryset.order_by('return_date', 'expire_date')

        return queryset


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
            change_message=gettext_lazy("Lease returned"))
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
    response['Content-Disposition'] = (
        'attachment; filename = "Report.xlsx"')

    workbook = build_xlsx()
    workbook.save(response)

    return response
