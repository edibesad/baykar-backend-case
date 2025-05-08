from rest_framework import serializers
from core.models.part_type import PartType
from core.models.team import Team


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["id", "name"]
        ref_name = "TeamInPartType"


class PartTypeSerializer(serializers.ModelSerializer):
    allowed_team = TeamSerializer(read_only=True)

    class Meta:
        model = PartType
        fields = ["id", "name", "allowed_team"]
        read_only_fields = ["id"]
        ref_name = "PartTypeDetail" 