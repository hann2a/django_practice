SSAFY 팀을 위한 Django 백엔드 빠른 스타터 가이드 (초보자용)

한 시간 내에 돌아가는 API를 만들고, ERD↔모델 매핑과 인증/문서화까지 맛보는 실습형 문서입니다.
Windows + Git Bash 기준으로 설명합니다. (cmd/PowerShell도 가능)

0. 개발환경 준비
0-1) 가상환경 생성 & 활성화

Git Bash:

python -m venv venv
source venv/Scripts/activate   # Git Bash/Mac/Linux
# venv\Scripts\activate        # cmd/PowerShell

0-2) 패키지 설치
pip install django djangorestframework

1. 프로젝트/앱 생성 & 실행
django-admin startproject backend_project
cd backend_project
python manage.py migrate                  # Django 기본 테이블 생성
python manage.py startapp stations        # 앱 생성
python manage.py runserver                # http://127.0.0.1:8000


폴더 구조(정상):

backend_project/
├─ manage.py
├─ db.sqlite3
├─ stations/
│  ├─ models.py / views.py / serializers.py / urls.py …
└─ backend_project/
   ├─ settings.py / urls.py …

2. ERD → Django 모델
2-1) ERD 개념

Station(역) — 1:N — Facility(편의시설)

Route(노선) — M:N — Station(역)

2-2) 모델 작성 — stations/models.py
from django.db import models

class Station(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200, blank=True)
    def __str__(self): return self.name

class Route(models.Model):
    name = models.CharField(max_length=100)
    stations = models.ManyToManyField(Station, related_name="routes", blank=True)
    def __str__(self): return self.name

class Facility(models.Model):
    name = models.CharField(max_length=100)
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="facilities")
    def __str__(self): return f"{self.name} @ {self.station.name}"


DB 반영:

python manage.py makemigrations
python manage.py migrate

3. 직렬화(Serializer)

stations/serializers.py

from rest_framework import serializers
from .models import Station, Route, Facility

class FacilitySerializer(serializers.ModelSerializer):
    # 쓰기용: station_id로 연결, 읽기는 station 필드로 출력
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
    facilities = FacilitySerializer(many=True, read_only=True)
    class Meta:
        model = Station
        fields = "__all__"

class RouteSerializer(serializers.ModelSerializer):
    # 쓰기용: station_ids
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

4. ViewSet + Router + URL 연결
4-1) ViewSet — stations/views.py
from rest_framework import viewsets, filters
from .models import Station, Route, Facility
from .serializers import StationSerializer, RouteSerializer, FacilitySerializer

class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "location"]     # /api/stations/?search=Seoul
    ordering_fields = ["id", "name"]         # /api/stations/?ordering=name

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

4-2) 앱 URL — stations/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StationViewSet, RouteViewSet, FacilityViewSet

router = DefaultRouter()
router.register(r'stations', StationViewSet, basename='station')
router.register(r'routes', RouteViewSet, basename='route')
router.register(r'facilities', FacilityViewSet, basename='facility')

urlpatterns = [ path('', include(router.urls)) ]

4-3) 프로젝트 URL — backend_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('stations.urls')),
]

4-4) DRF 기본 페이징(선택) — settings.py
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

5. 실행 & 테스트
python manage.py runserver


브라우저:

GET/POST: http://127.0.0.1:8000/api/stations/

GET/POST: http://127.0.0.1:8000/api/routes/

GET/POST: http://127.0.0.1:8000/api/facilities/

5-1) 예시 요청 페이로드

POST /api/stations/

{ "name": "Gangnam", "location": "Seoul" }


POST /api/routes/

{ "name": "Line 2", "station_ids": [1, 2] }


POST /api/facilities/

{ "name": "Restroom", "station_id": 1 }


화면 상단 파란 GET 버튼을 누르면 목록이 갱신됩니다.

6. Admin에서 데이터 관리(선택)

stations/admin.py

from django.contrib import admin
from .models import Station, Route, Facility
admin.site.register(Station)
admin.site.register(Route)
admin.site.register(Facility)

python manage.py createsuperuser


http://127.0.0.1:8000/admin/ 접속하여 데이터 생성/수정.

7. Swagger 문서(선택, 팀 공유용 강추)
7-1) 설치
pip install drf-yasg

7-2) URL 연결 — backend_project/urls.py
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.urls import path, include
from django.contrib import admin

schema_view = get_schema_view(
    openapi.Info(
        title="Transit API",
        default_version='v1',
        description="Stations/Routes/Facilities API",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('stations.urls')),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]


접속: http://127.0.0.1:8000/docs/

8. 인증: “읽기 공개, 쓰기는 로그인만” (JWT)
8-1) 설치
pip install djangorestframework-simplejwt

8-2) 설정 — backend_project/settings.py
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
}

8-3) URL — backend_project/urls.py
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns += [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

8-4) 사용 방법

브라우저에서 http://127.0.0.1:8000/api/token/ 접속

username/password로 POST → 응답의 access 복사

Postman에서 생성/수정/삭제 요청 시 헤더 추가:

Authorization: Bearer <access>
Content-Type: application/json


예: POST http://127.0.0.1:8000/api/stations/

{ "name": "Seocho", "location": "Seoul" }


Swagger를 쓰면 /docs/ → POST /api/token/로 토큰 받고, Authorize 버튼에 Bearer <access> 입력 후 Try it out.

브라우저 화면만 쓰고 싶다면 세션 인증도 병행 가능:

REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = (
    "rest_framework.authentication.SessionAuthentication",
    "rest_framework_simplejwt.authentication.JWTAuthentication",
)


그리고:

urlpatterns += [ path('api-auth/', include('rest_framework.urls')) ]


→ /api/... 화면 우상단 Log in으로 로그인 후 POST/PUT/DELETE 가능.

9. 자주 나는 오류 & 해결
404 /api/stations/

backend_project/urls.py에
path('api/', include('stations.urls')), 누락/오타

stations/urls.py 미생성 또는 Router 미등록

settings.py의 ROOT_URLCONF가 backend_project.urls가 아님

프로젝트 루트에 중복 urls.py 존재 → 삭제

Git Bash에서 가상환경 활성화 오류

source venv/Scripts/activate (슬래시 / 사용)

모델 바꿨는데 반영 안 됨

python manage.py makemigrations → python manage.py migrate

401/403 (쓰기 요청 실패)

헤더의 Authorization: Bearer <access> 누락/만료

새 토큰: POST /api/token/refresh/에 refresh 제출

10. 발표/문서용 요약 문구

“ERD(Station–Facility 1:N, Route–Station M:N)를 기준으로 Django 모델을 정의하고, DRF ViewSet/Router로 /stations, /routes, /facilities REST API를 구현했습니다. Browsable API와 Swagger로 테스트/문서화를 제공하고, IsAuthenticatedOrReadOnly + JWT를 적용해 읽기는 공개, 쓰기는 인증 필요 정책을 적용했습니다. 검색/정렬/페이징도 DRF 내장 기능으로 구성했습니다.”

부록: 빠른 테스트 스크립트 (curl)
# 목록
curl http://127.0.0.1:8000/api/stations/

# 토큰 발급
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"<pw>"}'

# 생성(토큰 넣기)
curl -X POST http://127.0.0.1:8000/api/stations/ \
  -H "Authorization: Bearer <access>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Gangnam","location":"Seoul"}'


필요하시면 이 문서를 README.md로 바로 붙여 넣을 수 있도록 추가 서식(목차/배지/.gitignore 등)도 만들어 드릴게요.