from rest_framework import serializers
from .models import Mission, MissionEvent
from drones.serializers import DroneSerializer


class MissionEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissionEvent
        fields = "__all__"


class MissionSerializer(serializers.ModelSerializer):
    assigned_drone_detail = DroneSerializer(source="assigned_drone", read_only=True)
    events = MissionEventSerializer(many=True, read_only=True)

    class Meta:
        model = Mission
        fields = "__all__"


class MissionCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=180)
    mission_type = serializers.CharField(max_length=40)
    region = serializers.CharField(max_length=40)
    priority = serializers.CharField(max_length=20, default="MEDIUM")
    drone_id = serializers.UUIDField()
    route_strategy = serializers.CharField(max_length=20, default="FASTEST")
