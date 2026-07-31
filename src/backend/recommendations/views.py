import logging

from django.db.models import Count, Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory.models import PieceRechange
from maintenance.models import InterventionPiece, LectureCapteur

from .groq_client import GroqNonConfigure, generer_recommandation

logger = logging.getLogger(__name__)


class RecommandationView(APIView):
    """
    Genere une recommandation en langage naturel a partir des KPI actuels (C6-C8, mission 7).

    GET /api/recommendations/  -> agrege les KPI puis appelle Groq (voir groq_client.py).
    Repli explicite (jamais de plantage silencieux) si le service IA n'est pas configure
    ou indisponible : renvoie les chiffres bruts avec un message clair.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        contexte = self._construire_contexte()

        try:
            texte = generer_recommandation(contexte)
            source = "groq"
        except GroqNonConfigure:
            logger.info("Recommandation IA non generee : service non configure.")
            texte = self._recommandation_repli(contexte)
            source = "repli_regles"
        except Exception as exc:  # noqa: BLE001 - on ne doit jamais planter l'endpoint
            logger.warning("Recommandation IA indisponible (%s), repli sur les regles.", exc)
            texte = self._recommandation_repli(contexte)
            source = "repli_regles"

        return Response({"source": source, "contexte": contexte, "recommandation": texte})

    @staticmethod
    def _construire_contexte() -> dict:
        # Filtre en Python (pas en SQL) car sous_le_seuil compare deux champs du meme
        # modele : Django ne le permet pas nativement sans F() ; le volume de pieces
        # reste faible, ce n'est pas un probleme de performance ici.
        pieces_sous_seuil = [
            {"nom": p.nom, "stock_actuel": p.stock_actuel, "seuil": p.seuil_reapprovisionnement}
            for p in PieceRechange.objects.all()
            if p.sous_le_seuil
        ]

        total_lectures = LectureCapteur.objects.count()
        total_pannes = LectureCapteur.objects.filter(panne=True).count()
        cout_total = InterventionPiece.objects.aggregate(total=Sum("cout_total"))["total"] or 0

        return {
            "taux_panne_pct": round(100 * total_pannes / total_lectures, 2) if total_lectures else 0,
            "cout_total_interventions": cout_total,
            "pieces_sous_seuil": pieces_sous_seuil,
        }

    @staticmethod
    def _recommandation_repli(contexte: dict) -> str:
        """Recommandation deterministe (regles) si le service IA est indisponible -
        garantit que l'endpoint reste utile meme sans cle Groq configuree."""
        if contexte["pieces_sous_seuil"]:
            noms = ", ".join(p["nom"] for p in contexte["pieces_sous_seuil"])
            return (
                f"Alerte stock : {noms} sous le seuil de reapprovisionnement. "
                f"Taux de panne actuel : {contexte['taux_panne_pct']}%. "
                "Recommandation (regle automatique) : lancer une commande de reapprovisionnement."
            )
        return (
            f"Aucune piece sous le seuil de reapprovisionnement. "
            f"Taux de panne actuel : {contexte['taux_panne_pct']}%. Situation stable."
        )
