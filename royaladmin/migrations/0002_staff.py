# Generated by Django 4.2 on 2024-11-28 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('royaladmin', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('passportimage', models.ImageField(blank=True, upload_to='staff_images/')),
                ('name', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
                ('gender', models.CharField(max_length=100)),
                ('desgination', models.CharField(max_length=100)),
            ],
        ),
    ]
