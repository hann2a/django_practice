# SSAFY 팀을 위한 Django 백엔드 빠른 스타터 가이드 (초보자용)

**목표:** 한 시간 내에 돌아가는 REST API를 만들고, **ERD ↔ 모델 매핑**, **CRUD**, **검색/정렬/페이징**까지 맛보는 실습형 가이드입니다.  
**환경:** Windows + Git Bash 기준 (cmd/PowerShell도 가능)

---

## 목차
- [0. 개발환경 준비](#0-개발환경-준비)
- [1. 프로젝트/앱 생성 & 실행](#1-프로젝트앱-생성--실행)
- [2. ERD → Django 모델](#2-erd--django-모델)
- [3. 직렬화(Serializers)](#3-직렬화serializers)
- [4. ViewSet + Router + URL](#4-viewset--router--url)
- [5. 실행 & 테스트](#5-실행--테스트)
---

## 0. 개발환경 준비

### 0-1) 가상환경 생성 & 활성화
Git Bash:
```bash
python -m venv venv
source venv/Scripts/activate    # Git Bash / Mac / Linux
# venv\Scripts\activate         # Windows cmd/PowerShell
```

### 0-2) 필수 패키지 설치
```bash
pip install django djangorestframework
```

## 1. 프로젝트/앱 생성 & 실행
```bash
django-admin startproject backend_project
cd backend_project
python manage.py migrate                  # Django 기본 테이블 생성
python manage.py startapp stations        # 앱 생성
python manage.py runserver                # http://127.0.0.1:8000
```
정상 폴더 구조 예시:
backend_project/
├─ manage.py
├─ db.sqlite3
├─ stations/
│  ├─ models.py / views.py / serializers.py / urls.py …
└─ backend_project/
   ├─ settings.py / urls.py …

## 2. ERD → Django 모델
### 2-1) ERD 개념(관계)
- Station(역) — 1:N — Facility(편의시설)
- Route(노선) — M:N — Station(역)

### 2-2) 모델 작성 — stations/models.py
```python 
from django.db import models

class Station(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name

class Route(models.Model):
    name = models.CharField(max_length=100)
    stations = models.ManyToManyField(Station, related_name="routes", blank=True)

    def __str__(self):
        return self.name

class Facility(models.Model):
    name = models.CharField(max_length=100)
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="facilities")

    def __str__(self):
        return f"{self.name} @ {self.station.name}"
```
DB 반영:
```bash
python manage.py makemigrations
python manage.py migrate
```

## 3. 직렬화(Serializers)
stations/serializers.py
```python 
from rest_framework import serializers
from .models import Station, Route, Facility

class FacilitySerializer(serializers.ModelSerializer):
    # 쓰기용: station_id로 연결 (읽기는 station 필드로 출력)
    station_id = serializers.PrimaryKeyRelatedField(
        queryset=Station.objects.all(),
        source="station",
        write_only=True
    )

    class Meta:
        model = Facility
        fields = ["id", "name", "station", "station_id"]
        read_only_fields = ["id", "station"]

class StationSerializer(serializers.ModelSerializer):
    # 역에 달린 편의시설 목록(읽기 전용)
    facilities = FacilitySerializer(many=True, read_only=True)

    class Meta:
        model = Station
        fields = "__all__"

class RouteSerializer(serializers.ModelSerializer):
    # 쓰기용: 역 ID 배열로 등록
    station_ids = serializers.PrimaryKeyRelatedField(
        queryset=Station.objects.all(),
        many=True,
        source="stations",
        write_only=True
    )
    # 읽기용: 역 상세
    stations = StationSerializer(many=True, read_only=True)

    class Meta:
        model = Route
        fields = ["id", "name", "stations", "station_ids"]
```

## 4. ViewSet + Router + URL
### 4-1) ViewSet — stations/views.py
```python 
from rest_framework import viewsets, filters
from .models import Station, Route, Facility
from .serializers import StationSerializer, RouteSerializer, FacilitySerializer

class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "location"]     # 예: ?search=Seoul
    ordering_fields = ["id", "name"]         # 예: ?ordering=name

class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().prefetch_related("stations")
    serializer_class = RouteSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "stations__name"]
    ordering_fields = ["id", "name"]

class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.select_related("station").all()
    serializer_class = FacilitySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "station__name"]
    ordering_fields = ["id", "name"]
```

### 4-2) 앱 URL — stations/urls.py
```python 
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
```

### 4-3) 프로젝트 URL — backend_project/urls.py
```python 
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('stations.urls')),
]
```

### 4-4) (선택) 전역 페이징 — backend_project/settings.py
```python 
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}
```

## 5. 실행 & 테스트
```bash 
python manage.py runserver
```

브라우저에서 아래 페이지로 이동(기본 Browsable API 제공):

- http://127.0.0.1:8000/api/stations/
- http://127.0.0.1:8000/api/routes/
- http://127.0.0.1:8000/api/facilities/

### 5-1) 예시 요청(POST) 페이로드
POST /api/stations/
```json
{ "name": "Gangnam", "location": "Seoul" }
```
POST /api/routes/
```json
{ "name": "Line 2", "station_ids": [1, 2] }
```
POST /api/facilities/
```json
{ "name": "Restroom", "station_id": 1 }
```
  화면 상단 파란 GET 버튼을 누르면 목록이 갱신됩니다.