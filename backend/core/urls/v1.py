from django.urls import path
from core.views.auth import AuthView, RefreshTokenView, MeView

urlpatterns = [
    path('auth/', AuthView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('me/', MeView.as_view(), name='me'),
]
