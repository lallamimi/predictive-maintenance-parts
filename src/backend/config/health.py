"""Endpoint de sante applicative (C11/C20)."""

import logging

from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    checks = {"database": False, "groq_configured": False}

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks["database"] = True
    except Exception as exc:  # noqa: BLE001
        logger.error("Health check DB failed: %s", exc)

    from django.conf import settings

    checks["groq_configured"] = bool(settings.GROQ_API_KEY)

    status_ok = checks["database"]
    return Response({"status": "ok" if status_ok else "degraded", "checks": checks}, status=200 if status_ok else 503)
