from django.urls import path

from api.views.drone_views import list_drones, get_drone
from api.views.mission_views import list_missions, get_mission, create_mission, mission_logs
from api.views.system_views import system_status, system_metadata

urlpatterns = [
    # Drones
    path("drones/", list_drones, name="list-drones"),
    path("drones/<str:drone_id>/", get_drone, name="get-drone"),

    # Missions
    path("missions/", list_missions, name="list-missions"),
    path("missions/create/", create_mission, name="create-mission"),
    path("missions/logs/", mission_logs, name="mission-logs"),
    path("missions/<str:mission_id>/", get_mission, name="get-mission"),

    # System
    path("system/status/", system_status, name="system-status"),
    path("system/metadata/", system_metadata, name="system-metadata"),
]
