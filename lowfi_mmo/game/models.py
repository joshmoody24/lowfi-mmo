from django.db import models
from django.contrib.auth.models import User
import uuid
from django.core.validators import RegexValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

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
        unique_together = [["owner", "name"]]
    
class WorldMember(models.Model):
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.user} - {self.world}"
    
class Entity(models.Model):
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    name = models.CharField(max_length=30, validators=[alphanumeric_validator]) # could be broken out
    def __str__(self):
        return self.name
    class Meta:
        abstract = True
        ordering = ['name']
        unique_together = [["world", "name"]]

class Area(models.Model):
    name = models.CharField(max_length=30, validators=[alphanumeric_validator])
    meters_per_unit = models.FloatField(validators=[MinValueValidator(0.0)])
    elevation = models.FloatField(default=0.0)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']
    
class Location(models.Model):
    LOCATION_TYPES = (("house", "house"), ("store", "store"))
    name = models.CharField(max_length=30, validators=[alphanumeric_validator])
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    x = models.FloatField()
    y = models.FloatField()
    description = models.TextField(blank=True)
    appearance = models.TextField(blank=True)
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPES, blank=True)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']
        unique_together = [["name", "area"]]

class Path(models.Model):
    name = models.CharField(max_length=30, blank=True, validators=[alphanumeric_validator])
    start = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="start_paths")
    end = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="end_paths")
    custom_distance = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0.0)])
    movement_cost_multiplier = models.FloatField(default=1.0, validators=[MinValueValidator(0.0)])
    description = models.CharField(max_length=100, blank=True)
    def clean(self):
        if self.start_id == self.end_id:
            raise ValidationError("Path start and end cannot be equal.")
    def __str__(self):
        return f"{(self.name + ': ') if self.name else ''}{self.start.name} -> {self.end.name}"
    class Meta:
        unique_together = [["start", "end"]]

class ItemPrefab(models.Model):
    name = models.CharField(max_length=30, validators=[alphanumeric_validator])
    description = models.TextField(blank=True)
    weight_kg = models.FloatField(default=1.0, validators=[MinValueValidator(0.0)])
    value = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00)])
    readable_message = models.TextField(max_length=500, null=True, blank=True)
    def __str__(self):
        return self.name
    
class CharacterPrefab(models.Model):
    name = models.CharField(max_length=30, validators=[alphanumeric_validator])
    gender = models.CharField(max_length=16, choices=(("M", "male"), ("F", "female"), ("nonbinary", "nonbinary")))
    appearance = models.TextField(max_length=200)
    personality = models.TextField(max_length=200)
    description = models.TextField(max_length=200)
    carry_limit = models.PositiveIntegerField(default=10)
    def __str__(self):
        return self.name
    class Meta:
        abstract = True
        ordering = ["name"]

class NpcPrefab(CharacterPrefab):
    # override name to be unique
    name = models.CharField(unique=True, max_length=30, validators=[alphanumeric_validator])
    owned_locations = models.ManyToManyField(Location, blank=True)

class CharacterInstance(models.Model):
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    items = models.ManyToManyField(ItemPrefab, through="InventoryItem")
    def __str__(self):
        maybe_player = Player.objects.filter(id=self.id).first()
        maybe_npc = NpcInstance.objects.filter(id=self.id).first()
        if(maybe_player):
            return str(maybe_player)
        elif(maybe_npc):
            return str(maybe_npc)
        else: return "unknown character instance"

class Player(CharacterPrefab):
    pass

class PlayerInstance(CharacterInstance):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    base = models.OneToOneField(Player, on_delete=models.CASCADE, related_name="traits")
    def __str__(self):
        return self.base.name
    class Meta:
        unique_together = [] # necessary due to weird Django inheritance rules
    
class NpcInstance(CharacterInstance):
    prefab = models.ForeignKey(NpcPrefab, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.prefab.name} - {self.world}" 
    # business logic unique constraint due to Django limitations
    def clean(self):
        if(NpcInstance.objects.filter(world=self.world, traits_id=self.traits_id).exclude(id=self.id).first() is not None):
            raise ValidationError("World can not have multiple NPCs with same prefab.")
    class Meta:
        # can't enforce unique traits per world due to Django inheritance rules
        unique_together = []

class ItemInstance(models.Model):
    item = models.ForeignKey(ItemPrefab, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=1)
    def __str__(self):
        return f"{self.item.name} x{self.quantity} instance"
    class Meta:
        abstract = True

class InventoryItem(ItemInstance):
    character = models.ForeignKey(CharacterInstance, on_delete=models.CASCADE)
    class Meta:
        unique_together = [["item", "character"]]

class DroppedItem(ItemInstance):
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    class Meta:
        unique_together = [["item", "location"]]

class Conversation(models.Model):
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    setting = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)
    start_time = models.DateTimeField(default=timezone.now)
    duration = models.DurationField()
    def __str__(self):
        return f"Conversation between {', '.join([str(participant) for participant in self.participants])} @ {self.setting}, {self.start_time}"

class ConversationParticipant(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="participants")
    character = models.ForeignKey(CharacterInstance, on_delete=models.CASCADE)
    join_delay = models.DurationField()
    def __str__(self):
        return str(self.character)
    class Meta:
        unique_together = [["conversation", "character"]]


''' TODO: inspect this structure more before implemented it (is a topic always 1:1 with another model?)
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
    relationship = models.TextField(blank=True)
    context_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    context_object_id = models.UUIDField()
    context_object = GenericForeignKey("context_type", "context_object_id")
    class Meta:
        indexes = [models.Index(fields=["context_type", "context_object_id"])]
'''