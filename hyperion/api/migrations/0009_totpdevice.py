# api/migrations/0009_totpdevice.py
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0008_simulationenvironment_simulationresult'),  
    ]

    operations = [
        migrations.CreateModel(
            name='TOTPDevice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.User')),
                ('name', models.CharField(max_length=64, default='default')),
                ('key', models.CharField(max_length=80)),
                ('confirmed', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_used', models.DateTimeField(null=True)),
            ],
            options={
                'verbose_name': 'TOTP Device',
                'verbose_name_plural': 'TOTP Devices',
            },
        ),
    ]