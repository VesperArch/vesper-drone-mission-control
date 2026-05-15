from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from core.singleton import MissionControlCenter
from core.enums import (
    DroneType,
    MissionType,
    RouteStrategyType,
    MaricaRegion,
    MissionPriority,
)


@api_view(["GET"])
def system_status(request: Request) -> Response:
    control = MissionControlCenter.get_instance()
    stats = control.get_statistics()

    recent_events = [
        {
            "mission_id": ev.mission_id,
            "event_type": ev.event_type,
            "message": ev.message,
            "timestamp": ev.timestamp.isoformat(),
        }
        for ev in control.get_event_log()[:20]
    ]

    return Response({
        "status": "ONLINE",
        "statistics": stats,
        "recent_events": recent_events,
    })


@api_view(["GET"])
def system_metadata(request: Request) -> Response:
    """Returns all enum options so the frontend can build forms dynamically."""
    return Response({
        "drone_types": [t.value for t in DroneType],
        "mission_types": [t.value for t in MissionType],
        "route_strategies": [t.value for t in RouteStrategyType],
        "regions": [r.value for r in MaricaRegion],
        "priorities": [p.value for p in MissionPriority],
    })
