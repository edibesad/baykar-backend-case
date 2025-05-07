from django.db import models
from .part_type import PartType
from .aircraft_model import AircraftModel
from .team import Team

class Part(models.Model):
    serial_number = models.CharField(max_length=100, unique=True)
    type = models.ForeignKey(PartType, on_delete=models.CASCADE)
    aircraft_model = models.ForeignKey(AircraftModel, on_delete=models.CASCADE)
    produced_by = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)
    is_recycled = models.BooleanField(default=False)
    used_in_aircraft = models.ForeignKey("Aircraft", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.serial_number} ({self.type.name})"
