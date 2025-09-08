from rest_framework import serializers
from .models import Station, Route, Facility

class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = "__all__"

class StationSerializer(serializers.ModelSerializer):
    facilities = FacilitySerializer(many=True, read_only=True)

    class Meta:
        model = Station
        fields = "__all__"

class RouteSerializer(serializers.ModelSerializer):
    # 쓰기용 ID 필드
    station_ids = serializers.PrimaryKeyRelatedField(
        queryset=Station.objects.all(),
        many=True,
        source="stations",
        write_only=True
    )
    # 읽기용 중첩
    stations = StationSerializer(many=True, read_only=True)

    class Meta:
        model = Route
        fields = ["id", "name", "stations", "station_ids"]