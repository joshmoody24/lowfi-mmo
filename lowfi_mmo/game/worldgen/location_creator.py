from game import models
from dataclasses import dataclass

def create_locations(world, data):
    paths = []
    for location_data in data["locations"]:
        location = models.Location.objects.create(world=world, appearance=location_data['appearance'], description=location_data['description'])
        add_names_and_tags(location, location_data)
        if not location_data.get('exits', False):
            raise Exception(f"Location \"{location_data['names'][0]}\" must have at least one exit path")
        for loc_exit in location_data['exits']:
            paths.append({'start_obj': location, 'exit': loc_exit})
    
    for path in paths:
        start = path['start_obj']
        end = models.Location.objects.get(world=world, names__name=path['exit']['to'])
        preposition = path['exit'].get('preposition', 'to')
        noun = path['exit'].get('noun', '')
        models.Path.objects.create(preposition=preposition, noun=noun, start=start, end=end) # TODO: optional travel_seconds

    for block_data in data["blocks"]:
        block = models.Block.objects.create(world=world, appearance=block_data['appearance'], description=block_data['description'])
        add_names_and_tags(block, block_data)
        one_way = block_data.get('one_way', False)
        starts = [block_data['from']] if one_way else [block_data['from'], block_data['to']]
        ends = [block_data['to']] if one_way else [block_data['from'], block_data['to']]
        blocked_paths = models.Path.objects.filter(start__world=world, end__world=world, start__names__name=starts, end__names__name=ends)
        for path in blocked_paths:
            block.paths.add(path)

    for key_data in data["keys"]:
        block = models.Block.objects.get(world=world, names__name=key_data['unlocks'])
        position = models.Location.objects.get(world=world, names__name=key_data['position'])
        key = models.Key.objects.create(world=world, description=key_data['description'], appearance=key_data['appearance'], unlocks=block, unlock_description=key_data['unlock_description'], position=position)
        add_names_and_tags(key, key_data)

def add_names_and_tags(entity, data):
    if not data.get('names', False):
        raise Exception(f"Entities must have at least one name")
    for name in data['names']:
        name_obj = models.Name.objects.create(world=entity.world, entity=entity, name=name)
        entity.names.add(name_obj)
    for tag in data.get('tags', []):
        tag_obj, _ = models.Tag.objects.get_or_create(name=tag)
        entity.tags.add(tag_obj)