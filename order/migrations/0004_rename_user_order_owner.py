# Generated by Django 4.2.6 on 2023-11-16 02:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0003_remove_order_city_remove_order_country_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='user',
            new_name='owner',
        ),
    ]