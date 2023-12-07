# Generated by Django 4.2.6 on 2023-11-15 20:00

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0029_remove_product_users_wishlist'),
        ('basket', '0002_remove_basket_products'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Cartitems',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1)),
                ('cart', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='basket.cart')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cartitems', to='store.product')),
            ],
        ),
        migrations.RemoveField(
            model_name='basketitem',
            name='basket',
        ),
        migrations.RemoveField(
            model_name='basketitem',
            name='product',
        ),
        migrations.DeleteModel(
            name='Basket',
        ),
        migrations.DeleteModel(
            name='BasketItem',
        ),
    ]
