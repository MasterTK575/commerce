# Generated by Django 4.2.3 on 2023-08-10 16:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_watchlist_added'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='watchlist',
            name='added',
        ),
    ]