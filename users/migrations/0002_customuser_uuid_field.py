# Generated by Django 4.2.6 on 2023-10-31 21:08

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='uuid_field',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]