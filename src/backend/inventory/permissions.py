from rest_framework.permissions import BasePermission

WRITE_ROLES = {"gestionnaire_stock", "admin"}


class IsGestionnaireOuAdmin(BasePermission):
    """
    Compétence C17 - gestion des droits et des accès.

    Lecture ouverte à tout utilisateur authentifié ; écriture (ajustement de
    stock) réservée aux rôles gestionnaire_stock et admin.
    """

    message = "Seuls les rôles gestionnaire_stock et admin peuvent modifier le stock."

    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return bool(request.user and request.user.is_authenticated)
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) in WRITE_ROLES
        )
