from django.urls import path
from .views import list_drones, get_drone, update_drone

urlpatterns = [
    path("", list_drones, name="list-drones"),
    path("<str:drone_id>/", get_drone, name="get-drone"),
    path("<str:drone_id>/status/", update_drone, name="update-drone"),
]
