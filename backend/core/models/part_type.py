from django.db import models
from .team import Team

class PartType(models.Model):
    name = models.CharField(max_length=50)
    allowed_team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='allowed_parts')

    def __str__(self):
        return f"{self.name} ({self.allowed_team.name})"
