from game import models
from django.db.transaction import atomic
import uuid
from .location_creator import create_locations
import tomllib
import os

@atomic
def populate_world(world):
    folder_path = os.path.dirname(os.path.abspath(__file__)) + '\\areas'
    world_data = compile_world_data(folder_path)
    create_locations(world, world_data)

def compile_world_data(folder_path):
    world_data = {}
    for file in os.listdir(folder_path):
        if(file.endswith('.toml')):
            file_path = os.path.join(folder_path, file)
            with open(file_path, 'rb') as file:
                file_data = tomllib.load(file)
                merge_lists(world_data, file_data)
    return world_data

def merge_lists(dict1, dict2):
    for key, value in dict2.items():
        if key in dict1 and isinstance(dict1[key], list) and isinstance(value, list):
            dict1[key].extend(value)
        else:
            dict1[key] = value

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