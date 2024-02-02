# Generated by Django 4.2.9 on 2024-02-01 05:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('babyapp', '0020_vaccinebooking'),
    ]

    operations = [
        migrations.CreateModel(
            name='VaccineStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_taken', models.BooleanField(default=False)),
                ('program', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='babyapp.vaccineprograms')),
            ],
        ),
    ]