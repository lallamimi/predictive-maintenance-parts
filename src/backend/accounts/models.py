from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Utilisateur avec role metier (C17 - gestion des droits et des acces)."""

    class Role(models.TextChoices):
        TECHNICIEN = "technicien", "Technicien de maintenance"
        GESTIONNAIRE_STOCK = "gestionnaire_stock", "Gestionnaire de stock"
        ADMIN = "admin", "Administrateur"

    role = models.CharField(max_length=32, choices=Role.choices, default=Role.TECHNICIEN)

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"
