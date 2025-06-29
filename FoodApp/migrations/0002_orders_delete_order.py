# Generated by Django 5.2 on 2025-05-08 07:17

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodApp', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(default='+91', max_length=13)),
                ('city', models.CharField(default=None, max_length=100)),
                ('state', models.CharField(default=None, max_length=100)),
                ('zipcode', models.CharField(default=None, max_length=100)),
                ('Address', models.TextField(default=None, max_length=200)),
                ('item_count', models.IntegerField()),
                ('item_price', models.IntegerField()),
                ('total_price', models.IntegerField()),
                ('order_date', models.DateField(default=django.utils.timezone.now)),
                ('rating', models.IntegerField(blank=True, default=0)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FoodApp.products')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='Order',
        ),
    ]
