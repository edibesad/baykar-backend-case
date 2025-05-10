from django.urls import path
from core.views.aircraft import AircraftViewSet
from core.views.auth import AuthView, RefreshTokenView, MeView
from core.views.part import PartViewSet
from core.views.part_type import PartTypeViewSet
from core.views.aircraft_model import AircraftModelViewSet

urlpatterns = [
    path("auth/", AuthView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", RefreshTokenView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path(
        "parts/", PartViewSet.as_view({"get": "list", "post": "create"}), name="parts"
    ),
    path(
        "parts/<int:pk>/",
        PartViewSet.as_view({"get": "retrieve", "delete": "destroy"}),
        name="parts-detail",
    ),
    path(
        "parts/stock/",
        PartViewSet.as_view({"get": "stock"}),
        name="parts-stock",
    ),
    path(
        "aircraft/",
        AircraftViewSet.as_view({"get": "list", "post": "create"}),
        name="aircraft",
    ),
    path(
        "aircraft/<int:pk>/",
        AircraftViewSet.as_view({"get": "retrieve", "delete": "destroy"}),
        name="aircraft-detail",
    ),
    path("part-types/", PartTypeViewSet.as_view({"get": "list"}), name="part-types"),
    path(
        "part-types/<int:pk>/",
        PartTypeViewSet.as_view({"get": "retrieve"}),
        name="part-types-detail",
    ),
    path(
        "aircraft-models/",
        AircraftModelViewSet.as_view({"get": "list"}),
        name="aircraft-models",
    ),
    path(
        "aircraft-models/<int:pk>/",
        AircraftModelViewSet.as_view({"get": "retrieve"}),
        name="aircraft-models-detail",
    ),
]
