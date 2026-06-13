from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from .models import Drone
from .serializers import DroneSerializer, DroneStatusUpdateSerializer


@api_view(["GET"])
def list_drones(request: Request) -> Response:
    return Response(DroneSerializer(Drone.objects.all(), many=True).data)


@api_view(["GET"])
def get_drone(request: Request, drone_id: str) -> Response:
    try:
        return Response(DroneSerializer(Drone.objects.get(id=drone_id)).data)
    except Drone.DoesNotExist:
        return Response({"error": "Drone not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(["PATCH"])
def update_drone(request: Request, drone_id: str) -> Response:
    """Called by mission-service to update drone status and battery after a mission."""
    try:
        drone = Drone.objects.get(id=drone_id)
    except Drone.DoesNotExist:
        return Response({"error": "Drone not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = DroneStatusUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if "status" in serializer.validated_data:
        drone.status = serializer.validated_data["status"]
    if "battery_level" in serializer.validated_data:
        drone.battery_level = serializer.validated_data["battery_level"]
    drone.save()

    return Response(DroneSerializer(drone).data)
