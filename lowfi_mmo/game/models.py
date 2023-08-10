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

def slugify_spaceless(entity):
    return slugify(str(entity)).replace("-", "")

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
    
class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True, validators=[alphanumeric_validator])
    def __str__(self):
        return self.name

class EntityQuerySet(models.QuerySet):
    def in_world(self, world):
        return self.filter(world=world)
    def at_location(self, location):
        return self.filter(position=location)
    def fuzzy_match(self, query):
        return self.filter(names__slug__iexact=slugify_spaceless(query))

class Entity(models.Model):
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    appearance = models.TextField(blank=True)
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag)
    objects: EntityQuerySet = EntityQuerySet.as_manager()
    @property
    def name(self):
        first_name = self.names.order_by('id').first()
        return first_name.name if first_name else "anonymous entity"
    @property
    def slug(self):
        first_name = self.names.first()
        return first_name.slug if first_name else "anonymous-entity"
    def __str__(self):
        return self.name

class Name(models.Model):
    name = models.CharField(max_length=20, validators=[alphanumeric_validator]) # could be broken out
    slug = models.SlugField(blank=True)
    world = models.ForeignKey(World, on_delete=models.CASCADE, related_name="names") # denormalized, curse you SQL
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="names")
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        self.slug = slugify_spaceless(self.name)
        super(Name, self).save(*args, **kwargs)
    class Meta:
        ordering = ['entity', 'name']
        unique_together = [["world", "slug"]]

class Mystery(models.Model):
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    connections = models.ManyToManyField("Mystery")

class Clue(models.Model):
    mystery = models.ForeignKey(Mystery, on_delete=models.CASCADE)
    summary = models.TextField()

class Location(Entity):
    LOCATION_CATEGORIES = (("house", "house"), ("store", "store"), ("secret", "secret"), ("other", "other"))
    category = models.CharField(max_length=20, choices=LOCATION_CATEGORIES, blank=True)
    arrive_clue = models.ForeignKey(Clue, null=True, blank=True, on_delete=models.SET_NULL, related_name="locations_arrive")
    search_clue = models.ForeignKey(Clue, null=True, blank=True, on_delete=models.SET_NULL, related_name="locations_search")

class PathQuerySet(models.QuerySet):
    def fuzzy_match_noun(self, noun):
        # TODO: when closer to release, use postgres trigram similarity instead of slugify_spaceless.
        return self.filter(noun_slug__iexact=slugify_spaceless(noun))
    def fuzzy_match_preposition(self, preposition):
        return self.filter(preposition__iexact=preposition)
    def fuzzy_match_destinations(self, noun):
        return self.filter(end__names__slug__iexact=slugify_spaceless(noun))

class Path(models.Model):
    preposition = models.CharField(max_length=20, blank=True, validators=[alphanumeric_validator])
    noun = models.CharField(max_length=20, blank=True, validators=[alphanumeric_validator])
    start = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="start_paths")
    end = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="end_paths")
    travel_seconds = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0.0)], default=10.0)
    noun_slug = models.SlugField(max_length=20) # for spaceless string matching
    hidden = models.BooleanField(default=False)
    discoverable = models.BooleanField(default=True)
    objects = PathQuerySet.as_manager()
    def save(self, *args, **kwargs):
        self.noun_slug = slugify_spaceless(self.noun)
        super(Path, self).save(*args, **kwargs)
    def clean(self):
        if self.start_id == self.end_id:
            raise ValidationError("Path start and end cannot be equal.")
        if(self.start.world_id != self.world_id or self.end.world_id != self.end.world_id):
            raise ValidationError("Path cannot connect locations from different worlds")
        if not self.preposition and not self.noun:
            raise ValidationError("Path needs a preposition, a noun, or both")
    def __str__(self):
        return f"{self.preposition}{' ' + self.noun if self.noun else ''}"
    class Meta:
        unique_together = [["start", "end", "preposition"], ["start", "preposition", "noun"]]

class Character(Entity):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    personality = models.TextField(max_length=200)
    carry_limit = models.PositiveIntegerField(default=10)
    position = models.ForeignKey(Location, on_delete=models.RESTRICT)
    path_taken = models.ForeignKey(Path, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    @property
    def carrying_weight(self):
        return self.item_set.aggregate(Sum("kg"))
    
class ClueKnowledge(models.Model):
    clue = models.ForeignKey(Clue, on_delete=models.CASCADE)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    
class CharacterLog(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    command = models.CharField(max_length=200)
    success = models.BooleanField(default=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    @property
    def css_class(self):
        if not self.success:
            return "error"
        elif self.command.startswith("go") or self.command.startswith("take"):
            return ""
        else: return ""
    def __str__(self):
        return self.message

class Item(Entity):
    kg = models.FloatField(default=1.0, validators=[MinValueValidator(0.0)])
    value = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00)])
    carrier = models.ForeignKey(Character, null=True, blank=True, on_delete=models.RESTRICT)
    position = models.ForeignKey(Location, null=True, blank=True, on_delete=models.RESTRICT)

    # inspectable
    inspect_clue = models.ForeignKey(Clue, null=True, blank=True, on_delete=models.SET_NULL, related_name="inspectable_from")

    # readable
    text = models.TextField(blank=True)
    text_clue = models.ForeignKey(Clue, null=True, blank=True, on_delete=models.SET_NULL, related_name="readable_from")

    def is_readable(self):
        return hasattr(self, 'text')

    def is_key(self):
        return hasattr(self, 'unlocks')
    
    def clean(self):
        if(self.carrier is None and self.position is None):
            raise ValidationError("Item carrier and location cannot both be null.")
        if(self.carrier is not None and self.position is not None):
            raise ValidationError("Item cannot have a carrier and location at the same time.")
        
class Block(Entity):
    paths = models.ManyToManyField(Path)
    active = models.BooleanField(default=True)
    unlocked_by = models.ForeignKey(Item, on_delete=models.CASCADE)
    unlock_description = models.TextField(blank=True)