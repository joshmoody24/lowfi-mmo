from django.db import transaction
from game import models

@transaction.atomic
def copy_world(world, new_name, new_owner):
    new_world = models.World(
        owner = new_owner,
        name = new_name
    )
    new_world.save()
    new_species = copy_species(world, new_world)
    new_items = copy_items(world, new_world)
    copied_map = copy_map(world.origin_map, new_items, new_species)

def copy_items(from_world, to_world):
    new_items_list = []
    for item in from_world.item_set.all():
        new_item = copy_object(item)
        new_item.world = to_world
        new_item.save()
        new_items_list.append(new_item)
    return new_items_list

def copy_species(from_world, to_world):
    new_species_list = []
    print("HEY")
    for species in from_world.species_set.all():
        new_species = copy_object(species)
        new_species.world = to_world
        new_species.save()
        new_species_list.append(new_species)
        print(new_species)
    return new_species_list

def copy_map(map, new_items, new_species, parent_location=None):
    # copy the map itself and all locations, and all characters in those locations
    new_map = copy_object(map)
    new_map.parent_location = parent_location
    new_map.save()
    for location in map.child_locations.all():
        new_location = copy_object(location)
        new_location.map = new_map
        new_location.save()
        for item_instance in location.iteminstance_set.all():
            new_item_instance = copy_object(item_instance)
            new_item_instance.owner = None # just in case
            new_item_instance.dropped_location = new_location
            new_item_instance.item = next([item for item in new_items if item.name == item_instance.item.name], None)
            new_item_instance.save()
        for character in location.character_set.filter():
            new_character = copy_object(character)
            new_character.location = new_location
            print(new_species)
            new_character.species = next((species for species in new_species if species.name == character.species.name), None)
            new_character.user = None
            new_character.save()
            for item_instance in character.iteminstance_set.all():
                new_item_instance = copy_object(item_instance)
                new_item_instance.owner = new_character
                new_item_instance.dropped_location = None # just in case
                new_item_instance.item = next((item for item in new_items if item.name == item_instance.item.name), None)
                new_item_instance.save()
        for location in location.child_maps.all():
            copy_map(map, new_items, new_species, new_location)

def copy_object(original_object):
    # Get the model class of the original object
    model_class = original_object.__class__

    # Get the list of fields for the model class
    fields = model_class._meta.fields

    # Create a new instance of the model
    copied_object = model_class()

    # Assign values from the original object to the copied object
    for field in fields:
        field_value = getattr(original_object, field.name)
        setattr(copied_object, field.name, field_value)

    # Optionally, clear the primary key to create a new database record
    copied_object.pk = None

    return copied_object