from django.db import models
from django.contrib.auth.models import User

# high-level geographical info for high-level gameplay

class Map(models.Model):
    location = models.ForeignKey("Location", null=True, on_delete=models.CASCADE, related_name="child_maps")
    name = models.CharField(max_length=50)
    traversal_type = models.CharField(max_length=20, choices=(("Unbounded", "Unbounded"),("Connections Only", "Connections Only")))
    meters_per_unit = models.FloatField(default=1)
    def __str__(self):
        return self.name

class Location(models.Model):
    map = models.ForeignKey(Map, on_delete=models.CASCADE, related_name="child_locations")
    name = models.CharField(max_length=100)
    x = models.FloatField()
    y = models.FloatField()
    description = models.TextField(blank=True)
    def __str__(self):
        return self.name + f" ({self.map})"
    
class LocationConnection(models.Model):
    location_from = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="source_locations")
    location_to = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="destination_locations")
    custom_distance = models.FloatField(null=True, blank=True)
    def __str__(self):
        return f"{self.location_from.name} -> {self.location_to.name}"
    class Meta:
        unique_together = [["location_from", "location_to"]]

# player models

class Species(models.Model):
    name = models.CharField(max_length=30)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "species"

class Character(models.Model):
    species = models.ForeignKey(Species, on_delete=models.RESTRICT)
    location = models.ForeignKey(Location, on_delete=models.RESTRICT)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL) # character becomes NPC
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    attack = models.IntegerField(null=True, blank=True)
    nutrition = models.IntegerField(null=True, blank=True)
    def __str__(self):
        return self.name

class ItemInstance(models.Model):
    item = models.ForeignKey(Item, on_delete=models.RESTRICT)
    custom_name = models.CharField(max_length=100, null=True, blank=True) # maybe blank instead?
    custom_description = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(Character, null=True, on_delete=models.SET_NULL)
    quantity = models.IntegerField(default=1)
    carried = models.BooleanField(default=True)
    dropped_location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)
    @property
    def name(self):
        return self.custom_name if self.custom_name else self.item.name
    @property
    def description(self):
        return self.custom_description if self.custom_description else self.item.description
    @property
    def location(self):
        return self.owner.location if self.owner else self.dropped_location
    def __str__(self):
        return f"{self.name} instance{'s' if self.quantity > 1 else ''} ({self.owner.name if self.owner else 'no owner'})"
    class Meta:
        unique_together = [["item", "owner"]]