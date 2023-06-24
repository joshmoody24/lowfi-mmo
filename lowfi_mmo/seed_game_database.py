import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lowfi_mmo.settings")
django.setup()

from django.db import migrations
from game.model_helpers import *
from game.models import World, Area, Location, ItemPrefab, ItemInstance, Entity
from django.contrib.auth.models import User
from django.db import transaction

import itertools

@transaction.atomic
def seed_database():

    existing_world = len(World.objects.all()) > 0
    if(existing_world):
        print("Existing data detected. Delete the database, run migrations, and then try again.")
        return

    # Create an initial superuser
    if not User.objects.filter(username='admin').exists():
        user = User.objects.create_superuser('admin', 'admin@fake.com', 'password')
        print("New admin user created")
    else:
        print("Admin already exists")

    # Create world
    world = World.objects.create(name='Bungerville', owner=User.objects.first())

    # Create town area
    town = Area.objects.create(world=world, name='Bungerville', meters_per_unit = 10)

    # main street
    grubbers = create_location(world, town, "Grubbers", -50, 0, 'A hole-in-the-wall burger joint.')
    wild_kingdom = create_location(world, town, 'Wild Kingdom', -40, 0, 'A wacky pet shop filled with many pungent odors.')
    flannel_tastic = create_location(world, town, 'Flanneltastic', -30, 0, 'A down-to-earth clothing store primarily known for its flannel shirts.')
    forgotten_pages = create_location(world, town, "Forgotten Pages", -20, 0, 'A store that collects and sells rare books.')
    big_jim_pizza = create_location(world, town, "Big Jim Pizza", -10, 0, 'The most popular pizza restaurant in town.')
    library = create_location(world, town, 'Library', 0, 0, 'The city library. It is fairly small, but packed to the rafters with books.')
    iced_creams = create_location(world, town, 'Iced Creams', 10, 0, 'A run-down ice cream shop.')

    # 100 S
    curiosity_corner = create_location(world, town, 'Curiosity Corner', -50, -10, 'A pawn shop that dabbles in just about everything.')
    astral_aura = create_location(world, town, 'Astral Aura', -40, -10, 'A spiritual shop for dedicated to improving people\'s auras through spirituality, meditation, and gemstones.')
    second_chances = create_location(world, town, 'Second Chances', -30, -10, 'A pawn shop that has an intense rivalry with Curiosity Corner, another pawn shop.')
    stockton_bank = create_location(world, town, 'Stockton Bank', -20, -10, 'A local bank that takes pride in serving farmers.')
    cineplex = create_location(world, town, 'The Cineplex', -10, -10, 'A run-down movie theater that is never sold out.')
    city_hall = create_location(world, town, 'City Hall', 0, -10, 'The political center of town.')
    unity_chapel = create_location(world, town, 'Unity Chapel', 10, -10, 'The largest church in town. It is made of pale yellow bricks and has a large steeple.')

    # main st paths
    create_path(world, grubbers, wild_kingdom)
    create_path(world, wild_kingdom, flannel_tastic)
    create_path(world, flannel_tastic, forgotten_pages)
    create_path(world, forgotten_pages, big_jim_pizza)
    create_path(world, big_jim_pizza, library)
    create_path(world, library, iced_creams)
    
    # 100 s paths
    create_path(world, curiosity_corner, astral_aura)
    create_path(world, astral_aura, second_chances)
    create_path(world, second_chances, stockton_bank)
    create_path(world, stockton_bank, cineplex)
    create_path(world, cineplex, city_hall)
    create_path(world, city_hall, unity_chapel)

    # cross-street paths
    create_path(world, grubbers, curiosity_corner)
    create_path(world, wild_kingdom, astral_aura)
    create_path(world, flannel_tastic, second_chances)
    create_path(world, forgotten_pages, stockton_bank)
    create_path(world, big_jim_pizza, cineplex)
    create_path(world, library, city_hall)

    # center street
    highway_39 = create_location(world, town, 'Highway 39', 0, 120, 'A highway that leads to Turtle Mountain.')
    game_haven = create_location(world, town, 'Game Haven', 0, 90, 'A game store that deals in card, board, and video games.')
    speedy_mart = create_location(world, town, 'Speedy Mart', 0, 80, 'A seedy convenience store with a single, run-down gas pump outside.')
    trendsetter_emporium = create_location(world, town, 'Trendsetter Emporium', 0, 70, 'A high-class fashion store.')
    high_school = create_location(world, town, 'High School', 0, 40, 'The town high school.')
    city_park = create_location(world, town, 'City Park', 0, 10, 'The city park, just north of the library.')
    market_masters = create_location(world, town, 'Market Masters', 0, -20, 'An advertising startup that has grown rapidly in recent years.')

    create_path(world, game_haven, speedy_mart)
    create_path(world, speedy_mart, trendsetter_emporium)
    create_path(world, trendsetter_emporium, city_park)
    create_path(world, city_park, library)
    create_path(world, library, market_masters)

    # where players live
    apartments = create_location(world, town, "Apartment Complex", -30, 30)
    create_path(world, apartments, library)
    create_path(world, apartments, city_park)
    create_path(world, apartments, high_school)

    # Create mountain area and link to town
    turtle_mountain = Area.objects.create(world=world, name='Turtle Mountain', meters_per_unit=1000)
    trailhead = create_location(world, turtle_mountain, 'Turtle Mountain Trailhead', 0, 0)
    water_treatment_plant = create_location(world, turtle_mountain, 'Water Treatment Plant', 0.25, 0.4)
    turtle_switchbacks = create_location(world, turtle_mountain, 'Switchbacks', 0.5, 0.5)
    turtle_falls = create_location(world, turtle_mountain, 'Turtle Falls', 1.25, 0.75)
    turtle_summit = create_location(world, turtle_mountain, 'Turtle Summit', 2, 0.8)
    turtle_cave = create_location(world, turtle_mountain, 'Turtle Cave', 2.5, 0.75)
    secret_bunker_entrance = create_location(world, turtle_mountain, 'Secret Bunker', 2.5, 0.75) # TODO: turn this into a path
    
    create_path(world, highway_39, trailhead)
    create_path(world, trailhead, water_treatment_plant)
    create_path(world, water_treatment_plant, turtle_switchbacks)
    create_path(world, turtle_switchbacks, turtle_falls)
    create_path(world, turtle_falls, turtle_summit)
    create_path(world, turtle_summit, turtle_cave)
    create_path(world, turtle_cave, secret_bunker_entrance)
    
    create_character(
        world,
        name="Grubby",
        location=grubbers,
        description="The owner of Grubster's Diner. Works long hours and is always willing to talk.",
        appearance="A short, stout middle aged man with a grease-stained apron and hair net",
        personality="Seems grumpy at first but quickly warms up to you. Very hardworking and focused.",
    )

    create_character(
        world,
        name="Josh",
        user=user,
        location=apartments,
        appearance="Blond hair",
        personality="A total jerk",
        description="The game dev",
    )

seed_database()