from game import models
from django.db.transaction import atomic
import uuid
import tomllib
import os
from django.db import IntegrityError
import glob

@atomic
def populate_world(world):
    containing_folder = os.path.dirname(os.path.abspath(__file__))

    # create locations
    locations_folder =  os.path.join(containing_folder, "locations")
    location_dicts = parse_all_toml_files(locations_folder)
    from .location_creator import create_locations
    create_locations(world, location_dicts)

    # create blocks
    blocks_dict = parse_toml_file(os.path.join(containing_folder, "blocks.toml"))
    for block_dict in blocks_dict["blocks"]:
        create_block(world, block_dict)

def parse_all_toml_files(directory):
    toml_files = glob.glob(f'{directory}/**/*.toml', recursive=True)
    toml_data = []
    for file_path in toml_files:
        toml_data.append(parse_toml_file(file_path))
    return toml_data

def parse_toml_file(file_path):
    with open(file_path, 'rb') as file:
        return tomllib.load(file)

def add_names_and_tags(db_entity, data):
    assert 'names' in data, f"Entities must have at least one name"
    for name in data['names']:
        try:
            name_obj = models.Name.objects.create(world=db_entity.world, entity=db_entity, name=name)
            db_entity.names.add(name_obj)
        except IntegrityError:
            raise IntegrityError(f"Entity with name \"{name}\" has already been created.")
    for tag in data.get('tags', []):
        tag_obj, _ = models.Tag.objects.get_or_create(name=tag)
        db_entity.tags.add(tag_obj)

def extract_details(dict):
    return {key: value for key, value in dict.items() if key in ["appearance", "description"]}

def create_block(world, block_dict):
    print(block_dict["unlocked_by"])
    key = models.Item.objects.in_world(world).get(names__name__iexact=block_dict["unlocked_by"])
    block_details = extract_details(block_dict)
    block = models.Block.objects.create(world=world, unlocked_by=key, **block_details)
    add_names_and_tags(block, block_dict)
    one_way = block_dict.get('one_way', False)
    starts = [block_dict['from']] if one_way else [block_dict['from'], block_dict['to']]
    ends = [block_dict['to']] if one_way else [block_dict['from'], block_dict['to']]
    blocked_paths = models.Path.objects.filter(start__world=world, end__world=world, start__names__name__in=starts, end__names__name__in=ends)
    if(blocked_paths.count() == 0): raise Exception(f"Block \"{block}\" has no paths")
    if(blocked_paths.count() > 2): raise Exception(f"Block \"{block}\" is blocking too many paths: " + ", ".join([str(path) + " (" + str(path.start) + " -> " + str(path.end) + ")" for path in blocked_paths])) # possibly temporary
    for path in blocked_paths:
        block.paths.add(path)