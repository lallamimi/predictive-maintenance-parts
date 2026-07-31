"""
URL configuration.

Deux espaces d'API bien separes (voir docs/architecture.md) :
  /api/data/...  -> acces aux donnees brutes (competence C5)
  /api/ml/...    -> exposition des modeles IA (competence C9, ajoute en tache suivante)
  /api/auth/...  -> authentification JWT
  /api/docs/...  -> documentation OpenAPI (drf-spectacular)
  /api/health/   -> sante applicative (C11/C20)
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .health import health_check

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/data/", include("inventory.urls")),
    path("api/data/", include("maintenance.urls")),
    path("api/", include("recommendations.urls")),
    path("api/health/", health_check, name="health-check"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
