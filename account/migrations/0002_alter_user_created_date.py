# Generated by Django 5.1 on 2024-09-16 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='created_date',
            field=models.DateField(auto_now_add=True),
        ),
    ]
