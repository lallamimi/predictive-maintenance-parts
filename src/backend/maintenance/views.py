from django.db.models import Count, Sum
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import InterventionPiece, LectureCapteur
from .serializers import InterventionPieceSerializer, LectureCapteurSerializer


class LectureCapteurViewSet(viewsets.ReadOnlyModelViewSet):
    """API donnees (C5) : consultation des lectures capteur / historique de pannes."""

    queryset = LectureCapteur.objects.all()
    serializer_class = LectureCapteurSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["panne", "type_produit"]


class InterventionPieceViewSet(viewsets.ReadOnlyModelViewSet):
    """API donnees (C5) : consultation des interventions de maintenance."""

    queryset = InterventionPiece.objects.select_related("piece", "lecture").all()
    serializer_class = InterventionPieceSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"])
    def kpi(self, request):
        """Indicateurs de performance (C14/C15) pour le tableau de bord decisionnel."""
        qs = self.get_queryset()
        total_lectures = LectureCapteur.objects.count()
        total_pannes = LectureCapteur.objects.filter(panne=True).count()

        par_piece = (
            qs.values("piece__nom")
            .annotate(nb=Count("id"), cout=Sum("cout_total"))
            .order_by("-cout")[:5]
        )

        return Response(
            {
                "nb_lectures_total": total_lectures,
                "nb_pannes": total_pannes,
                "taux_panne_pct": round(100 * total_pannes / total_lectures, 2) if total_lectures else 0,
                "nb_interventions": qs.count(),
                "cout_total_interventions": qs.aggregate(total=Sum("cout_total"))["total"] or 0,
                "top_pieces_par_cout": list(par_piece),
            }
        )
