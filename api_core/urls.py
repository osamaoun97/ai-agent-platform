from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from app.views.agents import AgentViewSet
from app.views.chatsession import ChatSessionViewSet
from app.views.home import home

schema_view = get_schema_view(
    openapi.Info(
        title="AI Agent Platform API",
        default_version="v1",
        description="API documentation for AI Agent project",
        contact=openapi.Contact(email="osamaoun997@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# DRF router
router = DefaultRouter()
router.register(r'agents', AgentViewSet, basename='agent')
router.register(r'sessions', ChatSessionViewSet, basename='session')

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("", home, name="home"),
    re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
