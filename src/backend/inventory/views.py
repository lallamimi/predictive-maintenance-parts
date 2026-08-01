import logging

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Fournisseur, PieceRechange
from .permissions import IsGestionnaireOuAdmin
from .serializers import AjusterStockSerializer, FournisseurSerializer, PieceRechangeSerializer

logger = logging.getLogger("inventory")


class FournisseurViewSet(viewsets.ReadOnlyModelViewSet):
    """API donnees (C5) : consultation des fournisseurs. Ecriture reservee au backoffice admin."""

    queryset = Fournisseur.objects.all()
    serializer_class = FournisseurSerializer
    permission_classes = [permissions.IsAuthenticated]


class PieceRechangeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API donnees (C5) : consultation des pieces de rechange et de leur stock.

    Competence C17 : la lecture est ouverte a tout utilisateur authentifie,
    l'ajustement de stock est reserve aux roles gestionnaire_stock/admin
    (voir IsGestionnaireOuAdmin, tests/test_permissions.py).
    """

    queryset = PieceRechange.objects.select_related("fournisseur").all()
    serializer_class = PieceRechangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == "ajuster_stock":
            return [IsGestionnaireOuAdmin()]
        return super().get_permissions()

    @action(detail=False, methods=["get"])
    def sous_seuil(self, request):
        """Pieces actuellement sous leur seuil de reapprovisionnement (alerte stock)."""
        qs = [p for p in self.get_queryset() if p.sous_le_seuil]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["patch"], url_path="ajuster-stock")
    def ajuster_stock(self, request, pk=None):
        """Ajuste le stock d'une piece (reception de commande, correction d'inventaire)."""
        piece = self.get_object()
        serializer = AjusterStockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ancien_stock = piece.stock_actuel
        piece.stock_actuel = serializer.validated_data["nouveau_stock"]
        piece.save(update_fields=["stock_actuel"])

        logger.info(
            "ajuster_stock user=%s piece=%s %d -> %d", request.user.username, piece.nom, ancien_stock, piece.stock_actuel
        )

        return Response(self.get_serializer(piece).data, status=status.HTTP_200_OK)
