# Generated by Django 4.2.6 on 2023-11-12 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0014_alter_product_brand'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='brand',
            field=models.CharField(default='', max_length=200),
        ),
    ]
