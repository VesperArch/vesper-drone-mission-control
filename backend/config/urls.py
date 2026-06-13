from django.urls import path, include

urlpatterns = [
    path("api/", include("adapters.urls.api_urls")),
]
