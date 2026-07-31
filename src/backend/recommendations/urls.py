from django.urls import path

from .views import RecommandationView

urlpatterns = [
    path("recommendations/", RecommandationView.as_view(), name="recommendations"),
]
