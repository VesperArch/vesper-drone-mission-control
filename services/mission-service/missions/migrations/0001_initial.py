import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Mission",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=180)),
                ("mission_type", models.CharField(max_length=40)),
                ("region", models.CharField(max_length=40)),
                ("priority", models.CharField(default="MEDIUM", max_length=20)),
                ("assigned_drone_id", models.CharField(blank=True, max_length=36, null=True)),
                ("route_strategy", models.CharField(default="FASTEST", max_length=20)),
                ("status", models.CharField(default="PENDING", max_length=20)),
                ("estimated_duration_min", models.FloatField(blank=True, null=True)),
                ("distance_km", models.FloatField(blank=True, null=True)),
                ("battery_consumption_pct", models.FloatField(blank=True, null=True)),
                ("weather_risk_score", models.FloatField(blank=True, null=True)),
                ("waypoints", models.JSONField(default=list)),
                ("route_notes", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="MissionEvent",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("mission", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="events", to="missions.mission")),
                ("event_type", models.CharField(max_length=30)),
                ("message", models.TextField()),
                ("severity", models.CharField(default="INFO", max_length=10)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-timestamp"]},
        ),
    ]
