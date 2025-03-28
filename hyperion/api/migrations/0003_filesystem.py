# Generated by Django 5.1.3 on 2024-12-05 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_cpuusage_memoryusage_networkusage'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileSystem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(max_length=20)),
                ('size', models.BigIntegerField()),
                ('modified_at', models.DateTimeField()),
                ('permissions', models.CharField(max_length=10)),
                ('owner', models.CharField(max_length=50)),
                ('group', models.CharField(max_length=50)),
            ],
        ),
    ]
