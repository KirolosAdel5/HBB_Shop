# Generated by Django 4.2.6 on 2023-11-09 23:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_tag_product_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='tags',
        ),
    ]