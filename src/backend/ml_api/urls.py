from django.urls import path

from .views import PredictDemandView, PredictFailureView

urlpatterns = [
    path("predict-failure/", PredictFailureView.as_view(), name="predict-failure"),
    path("predict-demand/", PredictDemandView.as_view(), name="predict-demand"),
]
