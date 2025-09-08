# stations/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StationViewSet, RouteViewSet, FacilityViewSet

router = DefaultRouter()
router.register(r'stations', StationViewSet, basename='station')
router.register(r'routes', RouteViewSet, basename='route')
router.register(r'facilities', FacilityViewSet, basename='facility')

urlpatterns = [
    path('', include(router.urls)),
]