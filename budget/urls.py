from django.contrib import admin
from django.urls import include
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView

from budget.utils.urls import Path

urlpatterns = [
    *Path("admin/", admin.site.urls, name="admin"),
    *Path("v2/", include("api2.urls")),
    *Path("o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    *Path("docs/schema/", SpectacularAPIView.as_view(), name="schema"),
    *Path(
        "docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"
    ),
    *Path("", include("django_prometheus.urls")),
]
