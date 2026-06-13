import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Drone",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=120)),
                ("model", models.CharField(max_length=120)),
                ("drone_type", models.CharField(max_length=30)),
                ("status", models.CharField(default="IDLE", max_length=20)),
                ("battery_level", models.FloatField(default=100.0)),
                ("speed_kmh", models.FloatField()),
                ("altitude_limit_m", models.FloatField()),
                ("payload_kg", models.FloatField()),
                ("range_km", models.FloatField()),
                ("description", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
    ]
