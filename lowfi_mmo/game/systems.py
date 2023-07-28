from game import models
from django.db.models import Sum, Max
from django.db import transaction

@transaction.atomic
def move(character, path_name): # todo: make this a traveler
    paths = models.Path.objects.filter(start=character.position)
    path = paths.filter(name__iexact=path_name).first()
    if(not path): return "", f"You cannot go \"{path_name}.\""

    # check for locks
    blocks = path.block_set.filter(active=True)
    if(blocks.count() > 0):
        return "", f"You could not go {path.name}. {' Additionally, '.join([block.description for block in blocks])}"
    
    character.position = path.end
    character.save()
    return f"{character.name} moved to {path.end}", ""
    
def look(character):
    location_description = character.position.description
    formatted_description = location_description[0].lower() + location_description[1:]
    return f"You look around. You see {formatted_description}.", ""

def take(character, item_name):
    item = models.Item.objects.filter(world=character.world, position=character.position, name__iexact=item_name).first()
    if(not item): return "", f"You don't see a nearby \"{item_name}.\""
    item.position = None
    item.carrier = character
    item.save()
    return f"You pick up {item.name}", ""

def use(character, item_name, entity_name):
    item = models.Item.objects.filter(world=character.world, carrier=character, name__iexact=item_name).first()
    entity = models.Entity.objects.filter(world=character.world, name__iexact=entity_name).first()
    if(not item): return "", f"You are not carrying an item named \"{item_name}.\""
    if(not entity or (hasattr(entity, 'position') and entity.position_id != character.position_id)): return "", f"There is no entity named \"{entity_name}\" nearby."

    maybe_key = models.Key.objects.filter(pk=item.id).first()
    nearby_paths = character.position.start_paths.all()
    maybe_block = models.Block.objects.filter(pk=entity.id, paths__in=nearby_paths).first()
    if maybe_key:
        if not maybe_block:
            print(f"There is no entity named \"{entity_name}\" nearby.")
        return unblock(maybe_key, maybe_block)
    
    return "", f"{item.name} cannot be used on {entity.name}"

def unblock(key, block):
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