from game import models
from django.db.models import Sum, Max
from django.db import transaction

@transaction.atomic
def move(entity, target_location): # todo: make this a traveler
    position = models.Position.objects.get(entity=entity)
    paths = models.Path.objects.filter(start=position.location)
    target_path = paths.filter(end__name__iexact=target_location).first()
    if(target_path):
        position.location = target_path.end
        position.save()
        return f"{entity.name} moved to {target_path.end}", ""
    else:
        if(target_location.lower() == position.location.name.lower()):
            return "", f"You are already at {position.location.name}"
        return "", f"No nearby location named \"{target_location}\""

@transaction.atomic
def attack(attacker_entity, defender_name, retaliation=False, battle_so_far=""):
    # make sure the defender exists and is in the same location as the attacker
    attacker_position = models.Position.objects.filter(entity=attacker_entity).first()
    defender_entity = models.Entity.objects.filter(name__iexact=defender_name).first()
    defender_position = models.Position.objects.filter(entity=defender_entity).first()
    if(attacker_position == None):
        return f"{attacker_entity.name} does not exist in the material realm and thus cannot attack.", ""
    if(defender_entity == None or defender_position.location_id != attacker_position.location_id):
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
        weapons = models.ItemInstance.objects.filter(inventory=attacker_inventory, item__attack__isnull=False)
        total_attack = weapons.aggregate(Sum('item__attack'))['item__attack__sum']
        if(total_attack is None): total_attack = 1

    # defense calculation
    defender_inventory = models.Inventory.objects.filter(entity=defender_entity).first()
    if(not defender_inventory):
        defenses = []
        total_defense = 0
    else:
        defenses = models.ItemInstance.objects.filter(inventory=defender_inventory, item__defense__isnull=False)
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