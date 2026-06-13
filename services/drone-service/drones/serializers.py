from rest_framework import serializers
from .models import Drone


class DroneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drone
        fields = "__all__"


class DroneStatusUpdateSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=20, required=False)
    battery_level = serializers.FloatField(required=False)
