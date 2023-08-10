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
    from .block_creator import create_block
    for block_dict in blocks_dict["blocks"]:
        create_block(world, block_dict)

    # create mysteries
    mystery_dicts = parse_all_toml_files(os.path.join(containing_folder, "mysteries"))
    from .mystery_creator import create_mysteries
    create_mysteries(world, mystery_dicts)


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