from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Fournisseur, PieceRechange
from .serializers import FournisseurSerializer, PieceRechangeSerializer


class FournisseurViewSet(viewsets.ReadOnlyModelViewSet):
    """API donnees (C5) : consultation des fournisseurs. Ecriture reservee au backoffice admin."""

    queryset = Fournisseur.objects.all()
    serializer_class = FournisseurSerializer
    permission_classes = [permissions.IsAuthenticated]


class PieceRechangeViewSet(viewsets.ReadOnlyModelViewSet):
    """API donnees (C5) : consultation des pieces de rechange et de leur stock."""

    queryset = PieceRechange.objects.select_related("fournisseur").all()
    serializer_class = PieceRechangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"])
    def sous_seuil(self, request):
        """Pieces actuellement sous leur seuil de reapprovisionnement (alerte stock)."""
        qs = [p for p in self.get_queryset() if p.sous_le_seuil]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
