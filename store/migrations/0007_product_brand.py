# Generated by Django 4.2.6 on 2023-11-09 23:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_remove_tag_products'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='brand',
            field=models.CharField(default='', max_length=200),
        ),
    ]
