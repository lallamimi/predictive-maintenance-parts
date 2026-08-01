from django.urls import path

from .views import ModelMonitoringView, PredictDemandView, PredictFailureView

urlpatterns = [
    path("predict-failure/", PredictFailureView.as_view(), name="predict-failure"),
    path("predict-demand/", PredictDemandView.as_view(), name="predict-demand"),
    path("monitoring/", ModelMonitoringView.as_view(), name="ml-monitoring"),
]
