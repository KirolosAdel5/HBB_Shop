# Generated by Django 4.2.6 on 2023-11-04 22:19

from django.db import migrations, models
import users.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_customuser_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='password',
            field=models.CharField(max_length=128, validators=[users.validators.validate_password_complexity], verbose_name='password'),
        ),
    ]