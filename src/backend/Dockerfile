FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# collectstatic n'est pas necessaire : ce conteneur ne sert que l'API (pas
# d'admin/templates exposes publiquement), et aucun mecanisme de service de
# fichiers statiques (whitenoise, nginx) n'est configure pour les consommer -
# l'inclure n'apportait rien et ajoutait un point d'echec possible au demarrage.
CMD ["sh", "-c", "python manage.py migrate --noinput && exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --log-level info"]
