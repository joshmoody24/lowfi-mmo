from game import models
import uuid

def create_character(
        world,
        name,
        appearance,
        personality,
        description,
        location,
        items=[],
        user=None,
    ):
    character = models.Character.objects.create(
        world=world,
        name=name,
        user=user,
        location=location,
        description=description,
        appearance=appearance, 
        personality=personality,
    )
    for item in items:
        character.items.add(item)
    return character

def create_path(world, start, end, two_way=True, name=""):
    paths = []
    paths.append(models.Path.objects.create(world=world, start=start, end=end, name=name))
    if(two_way): paths.append(models.Path.objects.create(world=world, start=end, end=start, name=name))
    return paths

def create_location(world, area, name, x, y, description=""):
    return models.Location.objects.create(world=world, area=area, name=name, x=x, y=y, description=description)

def create_item_type(world, name, description="", weight_kg=1.0, attack=None, defense=None):
    return models.ItemPrefab.objects.create(world=world, name=name, description=description, weight_kg=weight_kg, attack=attack, defense=defense)