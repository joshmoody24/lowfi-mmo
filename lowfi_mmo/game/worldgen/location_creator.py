from game import models
from dataclasses import dataclass
from django.db import IntegrityError

def create_locations(world, data):
    paths = []
    keys = []

    for location_data in data["locations"]:
        location = models.Location.objects.create(world=world, appearance=location_data['appearance'], description=location_data['description'])
        add_names_and_tags(location, location_data)
        if not location_data.get('exits', False):
            raise Exception(f"Location \"{location_data['names'][0]}\" must have at least one exit path")
        for loc_exit in location_data['exits']:
            paths.append({'start_obj': location, 'exit': loc_exit})
        for key_data in location_data.get("blocks", []):
            keys.append((location, key_data))
        for item_data in location_data.get("items", []):
            item = models.Item.objects.create(world=world, description=item_data['description'], appearance=item_data['appearance'], position=location)
            add_names_and_tags(item, item_data)

    for position, key_data in keys:
        block = models.Block.objects.get(world=world, names__name=key_data['unlocks'])
        position = models.Location.objects.get(world=world, names__name=key_data['position'])
        key = models.Key.objects.create(world=world, description=key_data['description'], appearance=key_data['appearance'], unlocks=block, unlock_description=key_data['unlock_description'], position=position)
        add_names_and_tags(key, key_data)

    for path in paths:
        start = path['start_obj']
        try:
            end = models.Location.objects.get(world=world, names__name__iexact=path['exit']['to'])
        except models.Location.DoesNotExist:
            raise models.Location.DoesNotExist(f"Location named \"{path['exit']['to']}\" does not exist.")
        preposition = path['exit'].get('preposition', 'to')
        noun = path['exit'].get('noun', '')
        if not preposition and not noun: raise Exception("Path must have a preposition or a noun")
        try:
            models.Path.objects.create(preposition=preposition, noun=noun, start=start, end=end, hidden=path.get('hidden', False)) # TODO: optional travel_seconds
        except IntegrityError:
            raise IntegrityError(f"{preposition if noun else '<no preposition>'}-{noun if noun else '<no noun>'} already exists for location {path['exit']['name']}")

    for block_data in data["blocks"]:
        block = models.Block.objects.create(world=world, appearance=block_data['appearance'], description=block_data['description'])
        add_names_and_tags(block, block_data)
        one_way = block_data.get('one_way', False)
        starts = [block_data['from']] if one_way else [block_data['from'], block_data['to']]
        ends = [block_data['to']] if one_way else [block_data['from'], block_data['to']]
        blocked_paths = models.Path.objects.filter(start__world=world, end__world=world, start__names__name__in=starts, end__names__name__in=ends)
        if(blocked_paths.count() == 0): raise Exception(f"Block \"{block}\" has no paths")
        if(blocked_paths.count() > 2): raise Exception(f"Block \"{block}\" is blocking too many paths: " + ", ".join([str(path) + " (" + str(path.start) + " -> " + str(path.end) + ")" for path in blocked_paths])) # possibly temporary
        for path in blocked_paths:
            block.paths.add(path)

def add_names_and_tags(entity, data):
    if not data.get('names', False):
        raise Exception(f"Entities must have at least one name")
    for name in data['names']:
        try:
            name_obj = models.Name.objects.create(world=entity.world, entity=entity, name=name)
            entity.names.add(name_obj)
        except IntegrityError:
            raise IntegrityError(f"Entity with name \"{name}\" has already been created.")
    for tag in data.get('tags', []):
        tag_obj, _ = models.Tag.objects.get_or_create(name=tag)
        entity.tags.add(tag_obj)