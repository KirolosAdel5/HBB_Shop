# Generated by Django 4.2.6 on 2023-11-14 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_wishlistitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(max_length=15, unique=True),
        ),
    ]
