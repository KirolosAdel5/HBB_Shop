# Generated by Django 4.2.6 on 2023-11-15 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basket', '0003_cart_cartitems_remove_basketitem_basket_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitems',
            name='quantity',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
