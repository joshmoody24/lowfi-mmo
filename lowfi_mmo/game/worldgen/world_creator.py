from game import models
from django.db.transaction import atomic
import uuid
from .location_creator import create_locations
import tomllib
import os

@atomic
def populate_world(world):
    with open(os.path.dirname(os.path.abspath(__file__)) + '/world.toml', 'rb') as file:
        world_data = tomllib.load(file)
    create_locations(world, world_data)

def create_character(
    name,
    appearance,
    personality,
    description,
    user=None,
):
    character = models.Character.objects.create(
        name=name,
        description=description,
        appearance=appearance, 
        personality=personality,
        user=user,
    )

def create_path(start, end, two_way=True, name=""):
    paths = []
    paths.append(models.Path.objects.create(start=start, end=end, name=name))
    if(two_way): paths.append(models.Path.objects.create(start=end, end=start, name=name))
    return paths

def create_item_type(world, name, description="", weight_kg=1.0, attack=None, defense=None):
    return models.ItemPrefab.objects.create(world=world, name=name, description=description, weight_kg=weight_kg, attack=attack, defense=defense)