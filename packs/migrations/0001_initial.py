# Generated by Django 5.1 on 2024-09-16 13:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0002_alter_user_created_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPackInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.PositiveIntegerField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='account.user')),
            ],
        ),
        migrations.CreateModel(
            name='UserPacks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pack_title', models.CharField(max_length=64)),
                ('pack_description', models.TextField()),
                ('given_date', models.DateField()),
                ('due_date', models.DateField()),
                ('user_pack_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='packs.userpackinfo')),
            ],
        ),
    ]
