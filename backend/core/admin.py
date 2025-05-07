from django.contrib import admin
from .models import (
    Team,
    Personnel,
    PartType,
    Part,
    AircraftModel,
    Aircraft,
)

admin.site.register(Team)
admin.site.register(Personnel)
admin.site.register(PartType)
admin.site.register(Part)
admin.site.register(AircraftModel)
admin.site.register(Aircraft)
