from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.utils.text import slugify

alphanumeric_validator = RegexValidator(
    r'^[a-zA-Z0-9\s\']*$',
    'Only alphanumeric characters, spaces and single quotes are allowed.'
)

class World(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    # TODO: timezone field somehow
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']
        unique_together = [["owner", "name"]]
    
class WorldMember(models.Model):
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.user} - {self.world}"
    
class Entity(models.Model):
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, validators=[alphanumeric_validator]) # could be broken out
    slug = models.SlugField(blank=True)
    appearance = models.TextField(blank=True)
    description = models.TextField(blank=True)
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Entity, self).save(*args, **kwargs)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']
        unique_together = [["world", "slug"]]
    
class Location(Entity):
    LOCATION_CATEGORIES = (("house", "house"), ("store", "store"), ("secret", "secret"), ("other", "other"))
    category = models.CharField(max_length=20, choices=LOCATION_CATEGORIES, blank=True)
    interior = models.BooleanField()
    def __str__(self):
        return self.name
    
# class LocationTag(models.Model):
#     LOCATION_TAGS = ["dark", "lit"]

class Path(models.Model):
    name = models.CharField(max_length=30, blank=True, validators=[alphanumeric_validator])
    start = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="start_paths")
    end = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="end_paths")
    travel_seconds = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0.0)], default=10.0)
    def clean(self):
        if self.start_id == self.end_id:
            raise ValidationError("Path start and end cannot be equal.")
        if(self.start.world_id != self.world_id or self.end.world_id != self.end.world_id):
            raise ValidationError("Path cannot connect locations from different worlds")
    def __str__(self):
        return f"{(self.name + ': ') if self.name else ''}{self.start.name} -> {self.end.name}"
    class Meta:
        unique_together = [["start", "end"]]

class Character(Entity):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    personality = models.TextField(max_length=200)
    carry_limit = models.PositiveIntegerField(default=10)
    position = models.ForeignKey(Location, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    @property
    def carrying_weight(self):
        return self.item_set.aggregate(Sum("kg"))
    def __str__(self):
        return self.name
    
class CharacterLog(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    command = models.CharField(max_length=200)
    success = models.BooleanField(default=True)
    result = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    @property
    def css_class(self):
        if not self.success:
            return "error"
        elif self.command.startswith("go "):
            return "success"
        else: return ""
    def __str__(self):
        return self.result

class Block(Entity):
    active = models.BooleanField(default=True)
    paths = models.ManyToManyField(Path)

class Item(Entity):
    kg = models.FloatField(default=1.0, validators=[MinValueValidator(0.0)])
    value = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00)])
    carrier = models.ForeignKey(Character, null=True, blank=True, on_delete=models.RESTRICT)
    position = models.ForeignKey(Location, null=True, blank=True, on_delete=models.RESTRICT)
    def clean(self):
        if(self.carrier is None and self.position is None):
            raise ValidationError("Item carrier and location cannot both be null.")
        if(self.carrier is not None and self.position is not None):
            raise ValidationError("Item cannot have a carrier and location at the same time.")
        
class Key(Item):
    unlocks = models.ForeignKey(Block, on_delete=models.CASCADE)
    unlock_description = models.TextField(blank=True)
        