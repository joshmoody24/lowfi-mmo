from game import models
from django.db.models import Sum, Max
from django.db import transaction

@transaction.atomic
def move(character, preposition, noun): # todo: make this a traveler
    if not preposition and not noun: return "", "Please specify where to go. Use <code>look</code> for nearby locations."

    path = None
    nearby_paths = models.Path.objects.filter(start=character.position)
    if(preposition and preposition.startswith('back') and not noun and character.previous_position):
        path = nearby_paths.filter(end=character.previous_position).first()
    elif noun and preposition:
        path = nearby_paths.filter(noun_slug__iexact=models.slugify_spaceless(noun), preposition__iexact=preposition).first()
        if not path: path = nearby_paths.filter(preposition__iexact=preposition, end__names__slug__iexact=models.slugify_spaceless(noun)).first()
    elif noun:
        path = nearby_paths.filter(noun_slug__iexact=models.slugify_spaceless(noun)).first()
        if not path: path = nearby_paths.filter(end__names__slug__iexact=models.slugify_spaceless(noun)).first()
    elif preposition and preposition not in ["to"]:
        possible_paths = nearby_paths.filter(preposition__iexact=preposition)
        if(possible_paths.count() == 1): path = possible_paths.first()

    if not path: return "", f"You cannot go {preposition if preposition else 'to'}{' ' + noun if noun else ''}"

    # check for locks
    blocks = path.block_set.filter(active=True)
    if(blocks.count() > 0):
        return "", f"You could not go {str(path)}. {' Additionally, '.join([block.description for block in blocks])}"
    
    character.previous_position = character.position
    character.position = path.end
    character.save()
    return f'<span class="success">You go {"back " if preposition == "back" else ""}{str(path)}.</span> ' + look(character, False)[0], ""
    
def look(character, describe_position=True):
    location_description = character.position.description
    formatted_description = location_description[0].lower() + location_description[1:]
    items = character.position.item_set.all()
    colored_item = lambda item: f'<span class="item">{str(item)}</span>'
    items_description = last_comma_to_and(f"Some nearby items include {', '.join([colored_item(item.name) for item in items])}.") if items.count() > 0 else ""
    new_paths = character.position.start_paths.exclude(end=character.previous_position)
    followed_path = character.position.start_paths.filter(end=character.previous_position).first()
    colored_path = lambda path: f'<span class="location">{str(path)}</span>'
    paths_description = last_comma_to_and("From here you can go " + ', '.join([colored_path(path) for path in new_paths]) + ".") if new_paths.count() > 0 else ""
    if followed_path and new_paths: paths_description += f" Or you can go back {colored_path(followed_path)}."
    elif followed_path: paths_description += f" From here you can go back {colored_path(followed_path)}."
    initial_message = f'<span class="success">You look around.</span> You are at {character.position.name}. ' if describe_position else ''
    return f"{initial_message}You see {formatted_description} {items_description} {paths_description}", ""

def take(character, item_name):
    item = models.Item.objects.filter(world=character.world, position=character.position, names__name__iexact=item_name).first()
    if(not item): return "", f"You don't see a nearby \"{item_name}\"."
    item.position = None
    item.carrier = character
    item.save()
    return f'You pick up <span class="item">{item.name}</span>', ""

def use(character, item_name, entity_name):
    item = models.Item.objects.filter(world=character.world, carrier=character, names__name__iexact=item_name).first()
    entity = models.Entity.objects.filter(world=character.world, names__name__iexact=entity_name).first()
    if not item: return "", f"You are not carrying an item named \"{item_name}.\""
    if not entity or (hasattr(entity, 'position') and entity.position_id != character.position_id): return "", f"There is no entity named \"{entity_name}\" nearby."

    # UNBLOCK SYSTEM
    maybe_key = models.Key.objects.filter(pk=item.id).first()
    nearby_paths = character.position.start_paths.all()
    maybe_block = models.Block.objects.filter(pk=entity.id, paths__in=nearby_paths).first()
    if maybe_key:
        if not maybe_block:
            return "", f"There is no entity named \"{entity_name}\" nearby."
        return unblock(maybe_key, maybe_block)
    
    return "", f'<span class="item">{item.name}</span> cannot be used on {entity.name}'

def unblock(key, block):
    if(key.unlocks != block): return "", f"You try to unlock {block.name} with {key.name}, but it doesn't work."
    if(block.active):
        block.active = False
        block.save()
        return key.unlock_description, ""
    else:
        return "", f"{block.name} was already unlocked" # TODO: make this message dynamic

@transaction.atomic
def attack(attacker_entity, defender_name, retaliation=False, battle_so_far=""):
    # make sure the defender exists and is in the same location as the attacker
    attacker_position = models.Position.objects.filter(entity=attacker_entity).first()
    defender_entity = models.Entity.objects.filter(name__iexact=defender_name).first()
    defender_position = models.Position.objects.filter(entity=defender_entity).first()
    if(attacker_position == None):
        return f"{attacker_entity.name} does not exist in the material realm and thus cannot attack.", ""
    if(defender_entity == None or defender_position.position_id != attacker_position.position_id):
        return f"{attacker_entity.name} looked around for {defender_name}, but couldn't find anyone by that name to attack.", ""
    
    # make sure defender is not already dead
    defender_health = models.Health.objects.filter(entity=defender_entity).first()
    if(defender_health and defender_health.hp <= 0):
        return f"{defender_entity.name} is already dead, but {attacker_entity.name} kicked them a few times just to be sure.", ""

    # TODO: make sure the attacker is capable of attacking

    # attack calculation
    attacker_inventory = models.Inventory.objects.filter(entity=attacker_entity).first()
    if(not attacker_inventory):
        weapons = []
        total_attack = 1
    else:
        weapons = models.DroppedItem.objects.filter(inventory=attacker_inventory, item__attack__isnull=False)
        total_attack = weapons.aggregate(Sum('item__attack'))['item__attack__sum']
        if(total_attack is None): total_attack = 1

    # defense calculation
    defender_inventory = models.Inventory.objects.filter(entity=defender_entity).first()
    if(not defender_inventory):
        defenses = []
        total_defense = 0
    else:
        defenses = models.DroppedItem.objects.filter(inventory=defender_inventory, item__defense__isnull=False)
        total_defense = defenses.aggregate(Sum('item__defense'))['item__defense__sum']
        if(total_defense is None): total_defense = 0

    # damage calculation
    damage = total_attack - total_defense
    if(damage < 1): damage = 1
    if(defender_health):
        defender_health.hp -= damage
        if(defender_health.hp < 0):
            defender_health.hp = 0
        defender_health.save()

    battle_so_far += f"""
    {attacker_entity.name} {'attacked' if retaliation == False else 'retaliated'} with {', '.join(list([x[0] for x in weapons.values_list('item__name')])) or 'their fists'}.
    {defender_entity.name} defended with {', '.join(list([x[0] for x in defenses.values_list('item__name')])) or 'their fists'}.
    {defender_entity.name} took {damage} damage{' and died' if defender_health and defender_health.dead else ''}.
    """

    if(not retaliation):
        battle_so_far, _ = attack(defender_entity, attacker_entity.name, retaliation=True, battle_so_far=battle_so_far)

    return battle_so_far, ""

def read(reader_character, readable):
    return f"{reader_character.entity.name} read {readable.entity.name}. It said: {readable.message}"

# handle oxford comma
def last_comma_to_and(comma_separated_list_str):
    return comma_separated_list_str[::-1].replace(', '[::-1], ', and '[::-1], 1)[::-1] # evil floating point string level hacking

# handle oxford comma
def last_comma_to_or(comma_separated_list_str):
    return comma_separated_list_str[::-1].replace(', '[::-1], ', or '[::-1], 1)[::-1] # evil floating point string level hacking