from django.db import models
from django.contrib.auth.models import User
import uuid
from django.core.validators import RegexValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

alphanumeric_validator = RegexValidator(
    r'^[a-zA-Z0-9\s\']*$',
    'Only alphanumeric characters, spaces and single quotes are allowed.'
)

class World(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=200, null=True, blank=True)
    # TODO: timezone field somehow
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']
    
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
    class Meta:
        ordering = ['name']
    
class Location(models.Model):
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, validators=[alphanumeric_validator], unique=True)
    x = models.FloatField()
    y = models.FloatField()
    description = models.TextField(blank=True)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']
    
class Path(models.Model):
    start = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="start_paths")
    end = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="end_paths")
    custom_distance = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0.0)])
    movement_cost_multiplier = models.FloatField(default=1.0, validators=[MinValueValidator(0.0)])
    name = models.CharField(max_length=30, blank=True)
    description = models.CharField(max_length=100, blank=True)
    def clean(self):
        if self.start == self.end:
            raise ValidationError("Path start and end cannot be equal.")
    def __str__(self):
        return f"{(self.name + ': ') if self.name else ''}{self.start.name} -> {self.end.name}"
    class Meta:
        unique_together = [["start", "end"]]

class Item(models.Model):
    name = models.CharField(max_length=30, validators=[alphanumeric_validator], unique=True)
    description = models.TextField(blank=True)
    weight_kg = models.FloatField(default=1.0, validators=[MinValueValidator(0.0)])
    value = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00)])
    readable_message = models.TextField(max_length=500, null=True, blank=True)
    def __str__(self):
        return self.name
    
class Clothing(models.Model):
    name = models.CharField(max_length=30)
    appearance = models.TextField(max_length=100)
    value = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, validators=[MinValueValidator(0.00)])
    def __str__(self):
        return self.name
    class Meta:
        abstract = True

class ClothingTop(Clothing):
    pass

class ClothingBottom(Clothing):
    pass

class ClothingAccessory(Clothing):
    pass

# entities + components (i.e. GameObjects)

class Entity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    name = models.CharField(max_length=30, validators=[alphanumeric_validator], unique=True) # could be broken out
    def __str__(self):
        return self.name
    class Meta:
        abstract = True
        ordering = ['name']

class Character(Entity):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    items = models.ManyToManyField(Item, through="InventoryItem")
    appearance = models.TextField(max_length=100)
    personality = models.TextField(max_length=100)
    carry_limit = models.PositiveIntegerField(default=10)

class Player(Character):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clothing_top = models.ForeignKey(ClothingTop, null=True, blank=True, on_delete=models.SET_NULL)
    clothing_bottom = models.ForeignKey(ClothingBottom, null=True, blank=True, on_delete=models.SET_NULL)
    clothing_accessory = models.ForeignKey(ClothingAccessory, null=True, blank=True, on_delete=models.SET_NULL)

class ClothingInstance(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    clothing = "Abstract Clothing"
    def __str__(self):
        return self.clothing
    class Meta:
        abstract = True
        unique_together=[["player", "clothing"]]

class ClothingTopInstance(ClothingInstance):
    clothing = models.ForeignKey(ClothingTop, on_delete=models.CASCADE)

class ClothingBottomInstance(ClothingInstance):
    clothing = models.ForeignKey(ClothingBottom, on_delete=models.CASCADE)
    
class ClothingAccessoryInstance(ClothingInstance):
    clothing = models.ForeignKey(ClothingAccessory, on_delete=models.CASCADE)

class Npc(Character):
    description = models.TextField(max_length=200)

class InventoryItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)

class ItemInstance(models.Model):
    item = models.ForeignKey(Item, on_delete=models.RESTRICT)
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=1)
    class Meta:
        unique_together = [["item", "location"]]

class Conversation(models.Model):
    setting = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)
    start_time = models.DateTimeField(default=timezone.now)
    duration = models.DurationField()
    def __str__(self):
        return f"Conversation between {', '.join([str(participant) for participant in self.participants])} @ {self.setting}, {self.start_time}"

class ConversationParticipant(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="participants")
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    join_delay = models.DurationField()
    def __str__(self):
        return str(self.character)
    class Meta:
        unique_together = [["conversation", "character"]]

class Topic(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class TopicConnection(models.Model):
    from_topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="source_topics")
    to_topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="destination_topics")
    def __str__(self):
        return f"{self.from_topic} -> {self.to_topic}"
    
class TopicContext(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    class Meta:
        abstract = True

class AreaContext(TopicContext):
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    def __str__(self):
        return f"Area context for {self.topic} ({self.area})"
    
class LocationContext(TopicContext):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    def __str__(self):
        return f"Location context for {self.topic} ({self.location})"
    
class NpcContext(TopicContext):
    npc = models.ForeignKey(Npc, on_delete=models.CASCADE)
    def __str__(self):
        return f"Npc context for {self.topic} ({self.npc})"
    
class ItemContext(TopicContext):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    def __str__(self):
        return f"Location context for {self.topic} ({self.item})"