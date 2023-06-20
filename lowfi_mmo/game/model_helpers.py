from game import models
import uuid

def create_player(
        world,
        name,
        user,
        appearance,
        personality,
        location,
        items=[],
        clothing_top=None,
        clothing_bottom=None,
        clothing_accessory=None
    ):
    player = models.Player.objects.create(
        world=world,
        name=name,
        user=user,
        location=location,
        clothing_top=clothing_top,
        clothing_bottom=clothing_bottom,
        clothing_accessory=clothing_accessory,
        appearance=appearance, 
        personality=personality,
    )
    for item in items:
        player.items.add(item)
    return player
    

def create_npc(
        world,
        name,
        appearance,
        personality,
        description,
        location,
        items=[],
    ):
    npc = models.Npc.objects.create(
        world=world,
        name=name,
        appearance=appearance, 
        location=location,
        personality=personality,
        description=description
    )
    for item in items:
        npc.items.add(item)
    return npc

def create_path(start, end, two_way=True, name=""):
    paths = []
    paths.append(models.Path.objects.create(start=start, end=end, name=name))
    if(two_way): paths.append(models.Path.objects.create(start=end, end=start, name=name))
    return paths

def create_location(area, name, x, y, description=""):
    return models.Location.objects.create(area=area, name=name, x=x, y=y, description=description)

def create_item_type(name, description="", weight_kg=1.0, attack=None, defense=None):
    return models.Item.objects.create(name=name, description=description, weight_kg=weight_kg, attack=attack, defense=defense)