from django.db import models
from .part_type import PartType
from .aircraft_model import AircraftModel
from .personnel import Personnel


class Part(models.Model):
    serial_number = models.CharField(max_length=100, unique=True)
    type = models.ForeignKey(PartType, on_delete=models.CASCADE)
    aircraft_model = models.ForeignKey(AircraftModel, on_delete=models.CASCADE)
    produced_by = models.ForeignKey(Personnel, on_delete=models.SET_NULL, null=True)
    used_in_aircraft = models.ForeignKey(
        "Aircraft",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="parts",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.serial_number} ({self.type.name})"
