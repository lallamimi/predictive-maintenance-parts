from rest_framework.routers import DefaultRouter

from .views import InterventionPieceViewSet, LectureCapteurViewSet

router = DefaultRouter()
router.register("lectures", LectureCapteurViewSet, basename="lecture")
router.register("interventions", InterventionPieceViewSet, basename="intervention")

urlpatterns = router.urls
