from django.db import models

# Create your models here.

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