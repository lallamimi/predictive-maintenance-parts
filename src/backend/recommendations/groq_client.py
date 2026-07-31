"""
Client Groq (competence C8 - paramétrage d'un service IA existant).

Justification du choix : voir docs/benchmark_ia.md.
Cle API : variable d'environnement GROQ_API_KEY (voir .env.example) - jamais en dur.
"""

from __future__ import annotations

import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = (
    "Tu es un assistant qui aide un gestionnaire de maintenance automobile a interpreter des "
    "indicateurs de stock et de panne. Reponds en francais, en 3 a 5 phrases courtes et concretes, "
    "sans jargon technique inutile. Base-toi uniquement sur les chiffres fournis, n'invente rien."
)


class GroqNonConfigure(Exception):
    """Levee quand GROQ_API_KEY n'est pas renseignee."""


def generer_recommandation(contexte: dict) -> str:
    """Envoie le contexte KPI/stock a Groq et retourne une recommandation en langage naturel.

    Leve GroqNonConfigure si la cle API est absente (permet a l'appelant de gerer
    proprement le cas, plutot que de planter silencieusement - voir recommendations/views.py).
    """
    if not settings.GROQ_API_KEY:
        raise GroqNonConfigure("GROQ_API_KEY n'est pas configuree (voir .env.example).")

    user_prompt = (
        "Voici les indicateurs actuels du systeme de maintenance :\n"
        f"{contexte}\n\n"
        "Redige une recommandation operationnelle courte pour le gestionnaire."
    )

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": 300,
        "temperature": 0.3,
    }
    headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}", "Content-Type": "application/json"}

    try:
        response = requests.post(GROQ_URL, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        texte = data["choices"][0]["message"]["content"].strip()
        logger.info("Recommandation Groq generee (%d caracteres).", len(texte))
        return texte
    except requests.exceptions.RequestException as exc:
        logger.error("Echec de l'appel Groq : %s", exc)
        raise
