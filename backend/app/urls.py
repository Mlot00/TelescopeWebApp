from django.urls import path

from .views import datasets, health, lightcurve, observations, skymap, spectrum, theta2

urlpatterns = [
    path("health", health),
    path("datasets", datasets),
    path("datasets/<str:dataset_id>/observations", observations),
    path("theta2", theta2),
    path("skymap", skymap),
    path("spectrum", spectrum),
    path("lightcurve", lightcurve),
]
