from django.conf.urls import url
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


def get_swagger_urls():
    schema_view = get_schema_view(
        openapi.Info(
            title="API",
            default_version='v1',
            description="GovReady API",
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
    )

    return [
        url(r'^docs/swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        url(r'^docs/swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    ]

