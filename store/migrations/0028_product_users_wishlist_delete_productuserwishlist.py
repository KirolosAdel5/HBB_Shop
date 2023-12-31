# Generated by Django 4.2.6 on 2023-11-14 21:18

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0027_remove_product_users_wishlist_productuserwishlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='users_wishlist',
            field=models.ManyToManyField(blank=True, related_name='user_wishlist', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='ProductUserWishlist',
        ),
    ]
