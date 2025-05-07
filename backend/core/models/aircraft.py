from django.db import models

from core.models.personnel import Personnel
from .aircraft_model import AircraftModel
from .part import Part


class Aircraft(models.Model):
    serial_number = models.CharField(max_length=100, unique=True)
    model = models.ForeignKey(AircraftModel, on_delete=models.CASCADE)
    assembled_by = models.ForeignKey(Personnel, on_delete=models.SET_NULL, null=True)
    assembled_at = models.DateTimeField(auto_now_add=True)
    wing = models.ForeignKey(
        Part,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wing_aircraft",
    )
    body = models.ForeignKey(
        Part,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="body_aircraft",
    )
    tail = models.ForeignKey(
        Part,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tail_aircraft",
    )
    avionic = models.ForeignKey(
        Part,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="avionic_aircraft",
    )
    engine = models.ForeignKey(
        Part,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="engine_aircraft",
    )

    def __str__(self):
        return f"{self.model.name} - {self.serial_number}"
