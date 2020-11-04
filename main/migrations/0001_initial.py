# Generated by Django 3.1.2 on 2020-11-04 12:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import isbn_field.fields
import isbn_field.validators
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('isbn', isbn_field.fields.ISBNField(max_length=28, primary_key=True, serialize=False, validators=[isbn_field.validators.ISBNValidator], verbose_name='ISBN')),
                ('name', models.CharField(max_length=255)),
                ('authors', models.CharField(max_length=255)),
                ('added_date', models.DateTimeField(auto_now_add=True)),
                ('count', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Lease',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('issue_date', models.DateTimeField(auto_now_add=True)),
                ('expire_date', models.DateField()),
                ('return_date', models.DateTimeField(null=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='main.book')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
