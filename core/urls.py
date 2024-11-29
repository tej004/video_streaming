from rest_framework.routers import DefaultRouter
from django.urls import path, include
from core.views import UserViewSet, VideoViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"videos", VideoViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
]
