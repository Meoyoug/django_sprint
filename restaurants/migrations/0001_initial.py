# Generated by Django 5.1.1 on 2024-09-26 07:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('type', models.CharField(choices=[('KOREAN', '한식'), ('CHINESE', '중식'), ('WESTERN', '양식'), ('JAPANESE', '일식'), ('OTHER', '기타')], max_length=10)),
                ('description', models.TextField(blank=True, null=True)),
                ('open_time', models.TimeField(blank=True, null=True)),
                ('close_time', models.TimeField(blank=True, null=True)),
                ('regular_holiday', models.CharField(blank=True, choices=[('MON', '월요일'), ('TUE', '화요일'), ('WED', '수요일'), ('THU', '목요일'), ('FRI', '금요일'), ('SAT', '토요일'), ('SUN', '일요일')], max_length=3, null=True)),
                ('last_order', models.TimeField(blank=True, null=True)),
                ('address', models.CharField(max_length=200)),
                ('contact', models.CharField(blank=True, max_length=50, null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='restaurants', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('image', models.ImageField(upload_to='images/menu')),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='menu', to='restaurants.restaurant')),
            ],
        ),
        migrations.CreateModel(
            name='RestaurantImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='images/restaurants')),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='restaurants.restaurant')),
            ],
        ),
    ]
