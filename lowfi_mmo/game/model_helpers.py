from game import models
import uuid

def create_character_prefab(
    name,
    appearance,
    personality,
    description,
    npc=True,
):
    traits_model = models.NpcPrefab if npc else models.PlayerTraits
    return traits_model.objects.create(
        name=name,
        description=description,
        appearance=appearance, 
        personality=personality,
    )

def instantiate_npc(
        character,
        world,
        location,
        traits,
        items=[],
    ):
    character = models.NpcInstance.objects.create(
        world=world,
        traits=traits,
        location=location,
    )
    for item in items:
        character.items.add(item)
    return character

def instantiate_player(
        character,
        world,
        location,
        traits,
        user,
        items=[],
    ):
    character = models.NpcInstance.objects.create(
        world=world,
        traits=traits,
        location=location,
        user=user,
    )
    for item in items:
        character.items.add(item)
    return character

def create_path(start, end, two_way=True, name=""):
    paths = []
    paths.append(models.Path.objects.create(start=start, end=end, name=name))
    if(two_way): paths.append(models.Path.objects.create(start=end, end=start, name=name))
    return paths

def create_location(area, name, x, y, description=""):
    return models.Location.objects.create(area=area, name=name, x=x, y=y, description=description)

def create_item_type(world, name, description="", weight_kg=1.0, attack=None, defense=None):
    return models.ItemPrefab.objects.create(world=world, name=name, description=description, weight_kg=weight_kg, attack=attack, defense=defense)