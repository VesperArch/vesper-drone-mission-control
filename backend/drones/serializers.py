from rest_framework import serializers
from .models import Drone


class DroneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drone
        fields = "__all__"
