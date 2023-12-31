from .world_creator import extract_details
from game import models
from .world_creator import add_names_and_tags
from collections import defaultdict

def create_mysteries(world, mystery_dicts):
    connections: defaultdict[models.Mystery, list[str]] = defaultdict(lambda: [])
    for mystery_dict in mystery_dicts:
        assert 'name' in mystery_dict, "Mysteries must be named"
        mystery = models.Mystery.objects.create(world=world, name=mystery_dict['name'])
        connections[mystery] += mystery_dict.get('connections', [])
        assert 'clues' in mystery_dict, f"{mystery} must have at least one clue"
        for clue_dict in mystery_dict["clues"]:
            assert 'summary' in clue_dict, f"{clue_dict} must have a summary"
            clue = models.Clue.objects.create(mystery=mystery, summary=clue_dict['summary'])
            # TODO: wire up the ways to discover the clue
            if('discoverable_at' in clue_dict):
                ...
            if('inspectable_from' in clue_dict):
                ...
            if('known_by' in clue_dict):
                ...
    
    for mystery, connections in connections.items():
        for connection in connections:
            mystery.connections.add(models.Mystery.objects.get(world=world, name__iexact=connection))