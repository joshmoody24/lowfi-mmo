from game import models
from django.db import IntegrityError
from .world_creator import add_names_and_tags, extract_details

def create_locations(world, locations):
    paths = []
    for location_dict in locations:
        location_db = create_location(world, location_dict)
        for loc_exit in location_dict['exits']:
            paths.append({'start_obj': location_db, 'exit': loc_exit})
        for item_dict in location_dict.get("items", []):
            create_item(world, item_dict, location_db)
    for path in paths:
        create_path(world, path)

def create_item(world, item_dict, position):
    item_details = extract_details(item_dict)
    item_db = models.Item.objects.create(world=world, position=position, **item_details)
    add_names_and_tags(item_db, item_dict)

def create_location(world, location_dict):
    assert 'exits' in location_dict, f"Location \"{str(location_dict)[:30] + '...'}\" must have at least one exit path"
    location_details = extract_details(location_dict)
    location_db = models.Location.objects.create(world=world, **location_details)
    add_names_and_tags(location_db, location_dict)
    return location_db

def create_path(world, path):
    start = path['start_obj']
    try:
        end = models.Location.objects.get(world=world, names__name__iexact=path['exit']['to'])
    except models.Location.DoesNotExist:
        raise models.Location.DoesNotExist(f"Location named \"{path['exit']['to']}\" does not exist.")
    preposition = path['exit'].get('preposition', 'to')
    noun = path['exit'].get('noun', '')
    assert preposition or noun, "Path must have a preposition or a noun"
    try:
        models.Path.objects.create(preposition=preposition, noun=noun, start=start, end=end, hidden=path.get('hidden', False)) # TODO: optional travel_seconds
    except IntegrityError:
        raise IntegrityError(f"{preposition if noun else '<no preposition>'}-{noun if noun else '<no noun>'} already exists for location {path['exit']['name']}")