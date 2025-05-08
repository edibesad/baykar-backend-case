from core.models.aircraft_model import AircraftModel
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from core.models import PartType


class IsTeamAuthorizedForPartType(BasePermission):
    message = "Takımınız bu parça türünü üretmeye yetkili değil."

    def has_permission(self, request, view):
        if request.method != "POST":
            return True

        user = request.user
        personnel = getattr(user, "personnel", None)

        if not personnel or not personnel.team:
            return False

        part_type_id = request.data.get("type_id")
        if not part_type_id:
            raise PermissionDenied("Parça türü belirtilmedi.")

        try:
            part_type = PartType.objects.get(id=part_type_id)
        except PartType.DoesNotExist:
            raise PermissionDenied("Geçersiz parça türü.")

        if part_type.allowed_team != personnel.team:
            raise PermissionDenied(self.message)

        return True


class IsTeamAuthorizedForAircraft(BasePermission):
    message = "Bu işlem için Montaj takımına ait olmanız gerekmektedir."

    def has_permission(self, request, view):
        user = request.user
        personnel = getattr(user, "personnel", None)

        if not personnel or not personnel.team:
            raise PermissionDenied(self.message)

        if personnel.team.responsibility.lower() != "montaj":
            raise PermissionDenied(self.message)

        return True
