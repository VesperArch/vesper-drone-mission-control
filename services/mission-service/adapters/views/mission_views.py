from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from missions.models import Mission, MissionEvent
from missions.serializers import MissionSerializer, MissionCreateSerializer, MissionEventSerializer
from core.facade.drone_mission_facade import DroneMissionFacade


@api_view(["GET"])
def list_missions(request: Request) -> Response:
    missions = Mission.objects.prefetch_related("events").all()
    return Response(MissionSerializer(missions, many=True).data)


@api_view(["GET"])
def get_mission(request: Request, mission_id: str) -> Response:
    try:
        mission = Mission.objects.prefetch_related("events").get(id=mission_id)
        return Response(MissionSerializer(mission).data)
    except Mission.DoesNotExist:
        return Response({"error": "Mission not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
def create_mission(request: Request) -> Response:
    serializer = MissionCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    facade = DroneMissionFacade()
    result = facade.create_and_start_mission(serializer.validated_data)

    if "error" in result:
        return Response(result, status=status.HTTP_409_CONFLICT)

    return Response(result, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def mission_logs(request: Request) -> Response:
    events = MissionEvent.objects.select_related("mission").order_by("-timestamp")[:100]
    return Response(MissionEventSerializer(events, many=True).data)
