import os
import sys
import django

sys.path.append(os.path.abspath('..'))  # Adjust the path if needed
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lowfi_mmo.settings")
django.setup()

from django.db import migrations
from model_helpers import create_character, create_path, create_location, create_item_type, instantiate_item
from game.models import World, Area, Location, Species, Item, ItemInstance, Entity
from django.contrib.auth.models import User
from django.db import transaction

@transaction.atomic
def seed_database():

    existing_world = len(World.objects.all()) > 0
    if(existing_world):
        print("Existing data detected. Delete the database, run migrations, and then try again.")

    # Create an initial superuser
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@fake.com', 'password')

    # Create world
    central_earth = World.objects.create(name='Central Earth', owner=User.objects.first())

    # Create overworld area
    overworld = Area.objects.create(world=central_earth, name='Overworld', meters_per_unit = 1000)

    castle = create_location(overworld, 'Central Earth Castle', 0, 0, 'A magnificent, regal, awe-inspiring castle in the center of the world')
    mogus_village = create_location(overworld, 'Mogus Village', 2, 1, 'A small village near the heartland')
    castle_town = create_location(overworld, 'Castle Town', 0, 0.5, 'A bustling metropolis just south of Central Earth Castle.')
    deathville = create_location(overworld, 'Deathville', -1, -2, 'A ghost town on the way to Boardoor. Evil spirits are rumored to haunt this land.')
    boardoor = create_location(overworld, 'Boardoor', -10, -20, 'An evil nation ruled by Earl: a giant glowing eyeball atop a menacing tower')

    create_path(castle, castle_town)
    create_path(mogus_village, deathville)
    create_path(deathville, boardoor)
    create_path(castle_town, mogus_village)

    central_earth.spawn_point = mogus_village
    mogus_village.save()

    # Create castle area and link to overworld
    castle_interior = Area.objects.create(world=central_earth, name='Central Earth Castle Interior', meters_per_unit=1)
    entrance = create_location(castle_interior, 'Castle Entrance', 0, 0)
    create_path(entrance, castle)

    armory = create_location(castle_interior, 'Armory', 50, 5)
    armory_trash_chute = create_location(castle_interior, 'Armory Trash Chute', 50, 0)
    throne_room = create_location(castle_interior, 'Throne Room', 0, 100)
    kitchen = create_location(castle_interior, 'Kitchen', -25, 25)
    library = create_location(castle_interior, 'Library', -50, 10)
    library_closet = create_location(castle_interior, 'Library Closet', -50, 12)

    create_path(entrance, armory)
    create_path(armory, armory_trash_chute, False)
    create_path(entrance, throne_room)
    create_path(entrance, library)
    create_path(library, library_closet)

    # Create dungeon area and link it to castle
    dungeon = Area.objects.create(world=central_earth, name='Central Earth Castle Dungeon', meters_per_unit=1, elevation=-20)
    trash_pile = create_location(dungeon, 'Trash Pile', -50, 10)
    prison_cells = create_location(dungeon, 'Prison Cells', 0, 0)
    create_path(armory_trash_chute, trash_pile)
    create_path(throne_room, prison_cells, name='Mysterious Trapdoor')

    execution_chamber = create_location(dungeon, 'Execution Chamber', 50, 0)
    evacuation_tunnel = create_location(dungeon, 'Secret Evacuation Tunnel', 50, -100)

    create_path(trash_pile, prison_cells)
    create_path(prison_cells, execution_chamber)
    create_path(execution_chamber, evacuation_tunnel)
    create_path(evacuation_tunnel, castle_town, False)

    # Species
    human = Species.objects.create(world=central_earth, name='Human')
    dwarf = Species.objects.create(world=central_earth, name='Dwarf')
    elf = Species.objects.create(world=central_earth, name='Elf')

    # Items
    broadsword = create_item_type(central_earth, 'Broadsword', description='A broadsword', attack=3)
    soup_ladel = create_item_type(central_earth, 'Soup Ladel', description='A large scooper for soup', attack=2)
    sharp_stone = create_item_type(central_earth, 'Sharp Stone', description='A stone with numerous sharp edges', attack=2)
    pitchfork = create_item_type(central_earth, 'Pitchfork', description='A large tool used by farmers', attack=3)
    longbow = create_item_type(central_earth, 'Longbow', description='A large bow with a seemingly infinite amount of arrows', attack=2)
    buckler = create_item_type(central_earth, 'Buckler', description='A simple shield', defense=1)
    chain_mail = create_item_type(central_earth, 'Chain Mail', description='Chain-linked defensive clothing', defense=1)
    apple = create_item_type(central_earth, 'Apple', description='A tasty snack', healing=1, weight_kg=0.1)
    big_gun = create_item_type(central_earth, 'MASSIVE *#@#%#^&* GUN', description='A huge freaking gun', attack=8)
    zombie_claws = create_item_type(central_earth, 'Zombie Claws', description='Zombie claws', attack=1)

    instantiate_item(central_earth, apple, dropped_location=trash_pile)

    create_character(central_earth, "Urist", dwarf, mogus_village, User.objects.first(), items=[broadsword, buckler])
    create_character(central_earth, "The Monarch", dwarf, throne_room, items=[chain_mail])
    create_character(central_earth, "Feetless", elf, prison_cells, items=[longbow])
    create_character(central_earth, "Farmer Joe", human, castle_town, items=[apple, apple, pitchfork])
    create_character(central_earth, "Boris", human, castle_town, items=[apple])
    create_character(central_earth, "Rabid Inmate", human, prison_cells, items=[sharp_stone])
    create_character(central_earth, "Carl the Cook", human, kitchen, items=[soup_ladel])
    create_character(central_earth, "Jimbo Swaggins", human, mogus_village, items=[apple])
    create_character(central_earth, "Fat Zombie", human, deathville, items=[zombie_claws, sharp_stone])
    create_character(central_earth, "Musculous Earl", human, boardoor, items=[big_gun, buckler])

seed_database()