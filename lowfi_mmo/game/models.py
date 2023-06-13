from django.db import models
from django.contrib.auth.models import User
import uuid
from django.core.validators import RegexValidator, MinValueValidator
from django.core.exceptions import ValidationError

alphanumeric_validator = RegexValidator(
    r'^[a-zA-Z0-9\s\']*$',
    'Only alphanumeric characters, spaces and single quotes are allowed.'
)

class World(models.Model):
    spawn_point = models.OneToOneField("Location", null=True, blank=True, on_delete=models.RESTRICT) # must be null when copying
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, validators=[alphanumeric_validator])
    template = models.BooleanField(default=False)
    def __str__(self):
        return self.name
    
class WorldMember(models.Model):
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.user} - {self.world}"
    
# high-level geographical info for high-level gameplay (i.e. Scenes)

class Area(models.Model):
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, validators=[alphanumeric_validator])
    meters_per_unit = models.FloatField(validators=[MinValueValidator(0.0)])
    elevation = models.FloatField(default=0.0)
    def __str__(self):
        return self.name

class Location(models.Model):
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, validators=[alphanumeric_validator])
    x = models.FloatField()
    y = models.FloatField()
    description = models.TextField(blank=True)
    def __str__(self):
        return self.name
    
class Path(models.Model):
    start = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="start_paths")
    end = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="end_paths")
    custom_distance = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0.0)])
    movement_cost_multiplier = models.FloatField(default=1.0, validators=[MinValueValidator(0.0)])
    name = models.CharField(max_length=30, blank=True)
    def clean(self):
        if self.start == self.end:
            raise ValidationError("Path start and end cannot be equal.")
    def __str__(self):
        return f"{(self.name + ': ') if self.name else ''}{self.start.name} -> {self.end.name}"
    class Meta:
        unique_together = [["start", "end"]]

# world-specific data (i.e. ScriptableObjects)

class Species(models.Model):
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    name = models.CharField(max_length=30, validators=[alphanumeric_validator])
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "species"
        unique_together = [["world", "name"]]

class Item(models.Model):
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    name = models.CharField(max_length=30, validators=[alphanumeric_validator])
    description = models.TextField(blank=True)
    weight_kg = models.FloatField(default=1.0, validators=[MinValueValidator(0.0)])
    # item capabilities
    # (could refactor using something like ECS down the road, if necessary)
    attack = models.IntegerField(null=True, blank=True)
    defense = models.IntegerField(null=True, blank=True)
    healing = models.IntegerField(null=True, blank=True)
    magic_cost = models.IntegerField(null=True, blank=True)
    def __str__(self):
        return self.name
    class Meta:
        unique_together = [["world", "name"]]

# entities + components (i.e. GameObjects)

class Entity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, validators=[alphanumeric_validator])
    class Meta:
        unique_together = [["world", "name"]]

class Component(models.Model):
    entity = models.OneToOneField(Entity, on_delete=models.CASCADE)
    def __str__(self):
        return self.entity.name
    class Meta:
        abstract = True

class Position(Component):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

class Character(Component):
    species = models.ForeignKey(Species, on_delete=models.RESTRICT)
    player = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL) # NPC if player is None

class CharacterKnowledge(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    KNOWLEDGE_TYPES = (("location", "location"), ("character", "character"), ("item_instance", "item_instance"))
    knowledge_type = models.CharField(max_length=20, choices=KNOWLEDGE_TYPES)
    knowledge = models.TextField()

class Killable(Component):
    max_hp = models.IntegerField(validators=[MinValueValidator(1)], default=10)
    hp = models.IntegerField(validators=[MinValueValidator(0)], default=10)
    # TODO: constrain hp to < max_hp (clean method?)

class MagicWielder(Component):
    max_mp = models.IntegerField(validators=[MinValueValidator(0)], default=10)
    mp = models.IntegerField(validators=[MinValueValidator(0)], default=10)

class Traveler(Component):
    path = models.ForeignKey(Path, null=True, blank=True, on_delete=models.SET_NULL)
    
class Inventory(Component):
    capacity = models.IntegerField(default=10.0, validators=[MinValueValidator(0)]) # max total item size

class Readable(Component):
    message = models.TextField()

class ItemInstance(Component):
    item = models.ForeignKey(Item, on_delete=models.RESTRICT)
    inventory = models.ForeignKey(Inventory, null=True, on_delete=models.SET_NULL)
    dropped_location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.CASCADE)