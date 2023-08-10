from game import models
from django.db.models import Sum, Max
from django.db import transaction
from dataclasses import dataclass

@dataclass
class Result:
    success: bool
    message: str

    @classmethod
    def succeed(cls, message=""):
        return cls(True, message)
    
    @classmethod
    def fail(cls, message=""):
        return cls(False, message)

@transaction.atomic
def move(character, preposition, noun) -> Result: # todo: make this a traveler
    if not preposition and not noun:
        return Result.fail("Please specify where to go. Use <code>look</code> for nearby locations.")

    path: models.Path | None = None
    
    nearby_paths: models.PathQuerySet = models.Path.objects.filter(start=character.position)
    if(preposition and preposition.startswith('back') and not noun and character.previous_position):
        print("if")
        path = nearby_paths.filter(end=character.previous_position).first()
    elif noun and preposition:
        print("elif 1")
        path = nearby_paths.fuzzy_match_noun(noun).fuzzy_match_preposition(preposition).first()
        if not path: path = nearby_paths.fuzzy_match_preposition(preposition).fuzzy_match_destinations(noun).first()
    elif noun:
        print("elif2", noun)
        path = nearby_paths.fuzzy_match_noun(noun).first()
        if not path: path = nearby_paths.fuzzy_match_destinations(noun).first()
    elif preposition and preposition not in ["to"]:
        print("here")
        possible_paths = nearby_paths.filter(preposition__iexact=preposition)
        if(possible_paths.count() == 1): path = possible_paths.first()

    if not path:
        return Result.fail(f"You cannot go {preposition if preposition else 'to'}{' ' + noun if noun else ''}")

    # check for locks
    blocks = path.block_set.filter(active=True)
    if(blocks.count() > 0):
        return Result.fail(f"You could not go {str(path)}. {' Additionally, '.join([block.description for block in blocks])}")
    
    character.previous_position = character.position
    character.position = path.end
    character.save()
    return Result.succeed(f'<span class="success">You go {"back " if preposition == "back" else ""}{str(path)}.</span> ' + look(character, False).message)
    
def look(character, describe_position=True):
    location_description = character.position.description
    formatted_description = location_description[0].lower() + location_description[1:]
    items = character.position.item_set.all()
    colored_item = lambda item: f'<span class="item">{str(item)}</span>'
    items_description = last_comma_to_and(f"Some nearby items include {', '.join([colored_item(item.name) for item in items])}.") if items.count() > 0 else ""
    available_paths = character.position.start_paths.exclude(hidden=True)
    colored_path = lambda path: f'<span class="location">{str(path)}</span>'
    paths_description = last_comma_to_and("From here you can go " + ', '.join([colored_path(path) for path in available_paths]) + ".") if available_paths.count() > 0 else ""
    initial_message = f'<span class="success">You look around.</span> You are at {character.position.name}. ' if describe_position else ''
    return Result.succeed(f"{initial_message}You see {formatted_description} {items_description} {paths_description}")

def take(character, item_name):
    item = models.Item.objects.at_location(character.position).fuzzy_match(item_name).first()
    if(not item): return Result.fail(f"You don't see a nearby \"{item_name}\".")
    item.position = None
    item.carrier = character
    item.save()
    return Result.succeed(f'You pick up <span class="item">{item.name}</span>')

def use(character, item_name, entity_name):
    item = models.Item.objects.filter(world=character.world, carrier=character, names__name__iexact=item_name).first()
    entity = models.Entity.objects.filter(world=character.world, names__name__iexact=entity_name).first()
    if not item:
        return Result.fail(f"You are not carrying an item named \"{item_name}.\"")
    if not entity or (hasattr(entity, 'position') and entity.position_id != character.position_id):
        return Result.fail(f"There is no entity named \"{entity_name}\" nearby.")

    # UNBLOCK SYSTEM
    maybe_key = models.Key.objects.filter(pk=item.id).first()
    nearby_paths = character.position.start_paths.all()
    maybe_block = models.Block.objects.filter(pk=entity.id, paths__in=nearby_paths).first()
    if maybe_key:
        if not maybe_block:
            return Result.fail(f"There is no entity named \"{entity_name}\" nearby.")
        return unblock(maybe_key, maybe_block)
    
    return Result.fail(f'<span class="item">{item.name}</span> cannot be used on {entity.name}')

def unblock(key, block):
    if(key.unlocks != block):
        return Result.fail(f"You try to unlock {block.name} with {key.name}, but it doesn't work.")
    if(block.active):
        block.active = False
        block.save()
        return Result.succeed(key.unlock_description)
    else:
        return Result.fail(f"{block.name} was already unlocked") # TODO: make this message dynamic

def read(reader_character, readable):
    return f"{reader_character.entity.name} read {readable.entity.name}. It said: {readable.message}"

# handle oxford comma
def last_comma_to_and(comma_separated_list_str):
    return comma_separated_list_str[::-1].replace(', '[::-1], ', and '[::-1], 1)[::-1] # evil floating point string level hacking

# handle oxford comma
def last_comma_to_or(comma_separated_list_str):
    return comma_separated_list_str[::-1].replace(', '[::-1], ', or '[::-1], 1)[::-1] # evil floating point string level hacking