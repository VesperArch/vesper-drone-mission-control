import uuid

from django.db import models

from core.enums import (
    MissionType,
    MissionStatus,
    MissionPriority,
    RouteStrategyType,
    MaricaRegion,
    EventType,
)
from drones.models import Drone


class Mission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=180)
    mission_type = models.CharField(
        max_length=40,
        choices=[(t.value, t.value) for t in MissionType],
    )
    region = models.CharField(
        max_length=40,
        choices=[(r.value, r.value) for r in MaricaRegion],
    )
    priority = models.CharField(
        max_length=20,
        choices=[(p.value, p.value) for p in MissionPriority],
        default=MissionPriority.MEDIUM,
    )
    assigned_drone = models.ForeignKey(
        Drone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="missions",
    )
    route_strategy = models.CharField(
        max_length=20,
        choices=[(s.value, s.value) for s in RouteStrategyType],
        default=RouteStrategyType.FASTEST,
    )
    status = models.CharField(
        max_length=20,
        choices=[(s.value, s.value) for s in MissionStatus],
        default=MissionStatus.PENDING,
    )
    estimated_duration_min = models.FloatField(null=True, blank=True)
    distance_km = models.FloatField(null=True, blank=True)
    battery_consumption_pct = models.FloatField(null=True, blank=True)
    weather_risk_score = models.FloatField(null=True, blank=True)
    waypoints = models.JSONField(default=list)
    route_notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} [{self.mission_type}] — {self.status}"


class MissionEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mission = models.ForeignKey(
        Mission,
        on_delete=models.CASCADE,
        related_name="events",
    )
    event_type = models.CharField(
        max_length=30,
        choices=[(e.value, e.value) for e in EventType],
    )
    message = models.TextField()
    severity = models.CharField(max_length=10, default="INFO")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"[{self.event_type}] {self.mission_id} — {self.message[:60]}"
