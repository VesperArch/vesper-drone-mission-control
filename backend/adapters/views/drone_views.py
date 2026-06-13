from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from drones.models import Drone
from drones.serializers import DroneSerializer


@api_view(["GET"])
def list_drones(request: Request) -> Response:
    drones = Drone.objects.all()
    return Response(DroneSerializer(drones, many=True).data)


@api_view(["GET"])
def get_drone(request: Request, drone_id: str) -> Response:
    try:
        drone = Drone.objects.get(id=drone_id)
        return Response(DroneSerializer(drone).data)
    except Drone.DoesNotExist:
        return Response({"error": "Drone not found."}, status=status.HTTP_404_NOT_FOUND)
