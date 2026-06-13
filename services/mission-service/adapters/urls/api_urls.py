from django.urls import path

from adapters.views.mission_views import list_missions, get_mission, create_mission, mission_logs
from adapters.views.system_views import system_status, system_metadata

urlpatterns = [
    path("missions/", list_missions, name="list-missions"),
    path("missions/create/", create_mission, name="create-mission"),
    path("missions/logs/", mission_logs, name="mission-logs"),
    path("missions/<str:mission_id>/", get_mission, name="get-mission"),
    path("system/status/", system_status, name="system-status"),
    path("system/metadata/", system_metadata, name="system-metadata"),
]
