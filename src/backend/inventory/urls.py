from rest_framework.routers import DefaultRouter

from .views import FournisseurViewSet, PieceRechangeViewSet

router = DefaultRouter()
router.register("fournisseurs", FournisseurViewSet, basename="fournisseur")
router.register("pieces", PieceRechangeViewSet, basename="piece")

urlpatterns = router.urls
