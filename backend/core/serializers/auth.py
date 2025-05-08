from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth.models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        "no_active_account": "Kullanıcı adı veya şifre hatalı.",
        "invalid_credentials": "Kullanıcı adı veya şifre hatalı.",
    }

    def validate(self, attrs):
        data = super().validate(attrs)

        # Kullanıcı bilgisi ekle
        user = self.user
        personnel = getattr(user, "personnel", None)

        data.update(
            {
                "user": {
                    "username": user.username,
                    "full_name": personnel.full_name if personnel else "",
                    "team": personnel.team.name if personnel else "",
                    "team_responsibility": (
                        personnel.team.responsibility if personnel else ""
                    ),
                }
            }
        )

        return data
