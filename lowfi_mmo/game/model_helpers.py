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
    entity = models.Entity.objects.create(world=world, name=name)
    position = models.Position.objects.create(entity=entity, location=location)
    models.Player.objects.create(
        user=user,
        entity=entity, 
        appearance=appearance, 
        personality=personality,
        clothing_top=instantiate_item(world, clothing_top),
        clothing_bottom=instantiate_item(world, clothing_bottom),
        clothing_accessory=instantiate_item(world, clothing_accessory),
    )
    inventory = models.Inventory.objects.create(entity=entity)
    for item in items:
        instantiate_item(world, item, inventory=inventory)
    models.Traveler.objects.create(entity=entity)
    return entity
    

def create_npc(
        world,
        name,
        appearance,
        personality,
        description,
        location,
        items=[],
    ):
    entity = models.Entity.objects.create(world=world, name=name)
    position = models.Position.objects.create(entity=entity, location=location)
    models.Npc.objects.create(
        entity=entity, 
        appearance=appearance, 
        personality=personality,
        description=description,
    )
    inventory = models.Inventory.objects.create(entity=entity)
    for item in items:
        instantiate_item(world, item, inventory=inventory)
    # models.Traveler.objects.create(entity=entity) # TODO: consider adding this
    return entity

def create_path(start, end, two_way=True, name=""):
    paths = []
    paths.append(models.Path.objects.create(start=start, end=end, name=name))
    if(two_way): paths.append(models.Path.objects.create(start=end, end=start, name=name))
    return paths

def create_location(area, name, x, y, description=""):
    return models.Location.objects.create(area=area, name=name, x=x, y=y, description=description)

def create_item_type(name, description="", weight_kg=1.0, attack=None, defense=None):
    return models.Item.objects.create(name=name, description=description, weight_kg=weight_kg, attack=attack, defense=defense)

def instantiate_item(world, item, inventory=None, dropped_location=None):
    if(item is None): return None
    if(inventory and dropped_location):
        raise Exception("Item instance cannot be in both an inventory and on the floor at the same time.")
    item_entity = models.Entity.objects.create(world=world, name=f'item-{uuid.uuid4()}')
    return models.ItemInstance.objects.create(entity=item_entity, item=item, inventory=inventory, dropped_location=dropped_location)