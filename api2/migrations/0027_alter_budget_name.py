# Generated by Django 4.0.1 on 2022-12-15 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api2', '0026_userinfo_darkmode_userinfo_theme'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budget',
            name='name',
            field=models.CharField(max_length=60),
        ),
    ]
