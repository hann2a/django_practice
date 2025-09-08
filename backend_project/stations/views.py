from rest_framework import viewsets, filters
from .models import Station, Route, Facility
from .serializers import StationSerializer, RouteSerializer, FacilitySerializer

class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    search_fields = ["name", "location"]      # ?search=Seoul
    ordering_fields = ["id", "name"]          # ?ordering=name

class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "stations__name"]
    ordering_fields = ["id", "name"]

class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer
    search_fields = ["name", "station__name"]
    ordering_fields = ["id", "name"]