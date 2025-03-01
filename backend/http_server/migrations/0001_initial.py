# Generated by Django 5.1.5 on 2025-02-05 01:11

import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Webhook',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('url', models.URLField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Website',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('url', models.URLField(unique=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('expected_status_code', models.IntegerField(default=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('associated_webhooks', models.ManyToManyField(blank=True, to='http_server.webhook')),
            ],
        ),
        migrations.CreateModel(
            name='StatusLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('up', 'UP'), ('down', 'DOWN')], max_length=10)),
                ('response_time', models.FloatField(null=True)),
                ('checked_at', models.DateTimeField(auto_now_add=True)),
                ('last_status_change', models.DateTimeField(default=django.utils.timezone.now)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='http_server.website')),
            ],
        ),
    ]
