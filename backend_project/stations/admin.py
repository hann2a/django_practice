from django.contrib import admin
from .models import Station, Route, Facility

admin.site.register(Station)
admin.site.register(Route)
admin.site.register(Facility)