import uuid

from django.db import models

from core.enums import DroneType, DroneStatus


class Drone(models.Model):
    """
    Persistent representation of a drone unit.
    Created via the Factory Method pattern; stored here for API queries.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)
    model = models.CharField(max_length=120)
    drone_type = models.CharField(
        max_length=30,
        choices=[(t.value, t.value) for t in DroneType],
    )
    status = models.CharField(
        max_length=20,
        choices=[(s.value, s.value) for s in DroneStatus],
        default=DroneStatus.IDLE,
    )
    battery_level = models.FloatField(default=100.0)
    speed_kmh = models.FloatField()
    altitude_limit_m = models.FloatField()
    payload_kg = models.FloatField()
    range_km = models.FloatField()
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} [{self.drone_type}] — {self.status}"
