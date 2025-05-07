from django.db import models
from .aircraft_model import AircraftModel
from .team import Team
from .part import Part

class Aircraft(models.Model):
    serial_number = models.CharField(max_length=100, unique=True)
    model = models.ForeignKey(AircraftModel, on_delete=models.CASCADE)
    assembled_by = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)
    assembled_at = models.DateTimeField(auto_now_add=True)
    parts = models.ManyToManyField(Part, related_name="aircrafts")

    def __str__(self):
        return f"{self.model.name} - {self.serial_number}"
