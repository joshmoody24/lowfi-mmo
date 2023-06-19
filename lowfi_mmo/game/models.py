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
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=200, null=True, blank=True)
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
    name = models.CharField(max_length=100, validators=[alphanumeric_validator], unique=True)
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

class Item(models.Model):
    DEFAULT = "default"
    CLOTHING_TOP = "clothing_top"
    CLOTHING_BOTTOM = "clothing_bottom"
    CLOTHING_ACCESSORY = "clothing_accessory"
    name = models.CharField(max_length=30, validators=[alphanumeric_validator], unique=True)
    description = models.TextField(blank=True)
    weight_kg = models.FloatField(default=1.0, validators=[MinValueValidator(0.0)])
    attack = models.PositiveIntegerField(null=True, blank=True)
    defense = models.PositiveIntegerField(null=True, blank=True)
    item_type_choices = (
        (DEFAULT, DEFAULT),
        (CLOTHING_TOP, CLOTHING_TOP),
        (CLOTHING_BOTTOM, CLOTHING_BOTTOM),
        (CLOTHING_ACCESSORY, CLOTHING_ACCESSORY),
    )
    item_type = models.CharField(max_length=20, choices=item_type_choices)
    def __str__(self):
        return self.name

# entities + components (i.e. GameObjects)

class Entity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, validators=[alphanumeric_validator]) # could be broken out
    def __str__(self):
        return self.name
    class Meta:
        unique_together = [["world", "name"]]

class Component(models.Model):
    entity = models.OneToOneField(Entity, on_delete=models.CASCADE)
    def __str__(self):
        return self.entity.name
    class Meta:
        abstract = True

class Character(Component):
    appearance = models.TextField(max_length=100)
    personality = models.TextField(max_length=100)
    class Meta:
        abstract = True

class Clothing(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    appearance = models.CharField(max_length=100)
    class Meta:
        abstract = True

class ClothingTop(Clothing):
    pass

class ClothingBottom(Clothing):
    pass

class ClothingAccessory(Clothing):
    pass

class Player(Character):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clothing_top = models.ForeignKey(ClothingTop, null=True, blank=True, on_delete=models.SET_NULL)
    clothing_bottom = models.ForeignKey(ClothingBottom, null=True, blank=True, on_delete=models.SET_NULL)
    clothing_accessory = models.ForeignKey(ClothingAccessory, null=True, blank=True, on_delete=models.SET_NULL)

class Npc(Character):
    description = models.TextField(max_length=200)

class Position(Component):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

class Health(Component):
    max_hp = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=10)
    hp = models.PositiveIntegerField(default=10)
    @property
    def dead(self):
        return self.hp <= 0
    # TODO: constrain hp to < max_hp (clean method?)

class Traveler(Component):
    path = models.ForeignKey(Path, null=True, blank=True, on_delete=models.SET_NULL)
    
class Inventory(Component):
    capacity = models.PositiveIntegerField(default=10.0) # max total item size

class Readable(Component):
    message = models.TextField(max_length=500)

class ItemInstance(Component):
    item = models.ForeignKey(Item, on_delete=models.RESTRICT)
    inventory = models.ForeignKey(Inventory, null=True, blank=True, on_delete=models.SET_NULL)
    dropped_location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=1)