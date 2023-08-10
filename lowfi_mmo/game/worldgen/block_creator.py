from .world_creator import extract_details
from game import models
from .world_creator import add_names_and_tags

def create_block(world, block_dict):
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