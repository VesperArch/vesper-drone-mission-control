from django.urls import path, include

urlpatterns = [
    path("api/drones/", include("drones.urls")),
]
