from game import models
import uuid

def clamp(number, min, max):
    return min(max(min, number), max)

def create_character(world, name, species, location, player=None, items=[]):
    entity = models.Entity.objects.create(world=world, name=name)
    models.Position.objects.create(entity=entity, location=location)
    models.Killable.objects.create(entity=entity)
    models.Character.objects.create(entity=entity, species=species, player=player)
    inventory = models.Inventory.objects.create(entity=entity)
    for item in items:
        instantiate_item(world, item, inventory=inventory)
    if(player): # just for simplicity
        models.Traveler.objects.create(entity=entity)
    return entity

def create_path(start, end, two_way=True, name=""):
    paths = []
    paths.append(models.Path.objects.create(start=start, end=end, name=name))
    if(two_way): paths.append(models.Path.objects.create(start=end, end=start, name=name))
    return paths

def create_location(area, name, x, y, description=""):
    return models.Location.objects.create(area=area, name=name, x=x, y=y, description=description)

def create_item_type(world, name, description="", weight_kg=1.0, attack=None, defense=None, healing=None):
    return models.Item.objects.create(world=world, name=name, description=description, weight_kg=weight_kg, attack=attack, defense=defense, healing=healing)

def instantiate_item(world, item, inventory=None, dropped_location=None):
    if(inventory and dropped_location):
        raise Exception("Item instance cannot be in both an inventory and on the floor at the same time.")
    item_entity = models.Entity.objects.create(world=world, name=f'item-{uuid.uuid4()}')
    return models.ItemInstance.objects.create(entity=item_entity, item=item, inventory=inventory, dropped_location=dropped_location)