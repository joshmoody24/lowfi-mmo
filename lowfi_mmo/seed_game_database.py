import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lowfi_mmo.settings")
django.setup()

from django.db import migrations
from game.model_helpers import *
from game.models import World, Area, Location, ItemPrefab, DroppedItem, Entity
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
    town = Area.objects.create(name='Bungerville', meters_per_unit = 10)

    # main street
    grubbers = create_location(town, "Grubbers", -50, 0, 'A hole-in-the-wall burger joint.')
    wild_kingdom = create_location(town, 'Wild Kingdom', -40, 0, 'A wacky pet shop filled with many pungent odors.')
    flannel_tastic = create_location(town, 'Flanneltastic', -30, 0, 'A down-to-earth clothing store primarily known for its flannel shirts.')
    forgotten_pages = create_location(town, "Forgotten Pages", -20, 0, 'A store that collects and sells rare books.')
    big_jim_pizza = create_location(town, "Big Jim Pizza", -10, 0, 'The most popular pizza restaurant in town.')
    library = create_location(town, 'Library', 0, 0, 'The city library. It is fairly small, but packed to the rafters with books.')
    iced_creams = create_location(town, 'Iced Creams', 10, 0, 'A run-down ice cream shop.')

    # 100 S
    curiosity_corner = create_location(town, 'Curiosity Corner', -50, -10, 'A pawn shop that dabbles in just about everything.')
    astral_aura = create_location(town, 'Astral Aura', -40, -10, 'A spiritual shop for dedicated to improving people\'s auras through spirituality, meditation, and gemstones.')
    second_chances = create_location(town, 'Second Chances', -30, -10, 'A pawn shop that has an intense rivalry with Curiosity Corner, another pawn shop.')
    stockton_bank = create_location(town, 'Stockton Bank', -20, -10, 'A local bank that takes pride in serving farmers.')
    cineplex = create_location(town, 'The Cineplex', -10, -10, 'A run-down movie theater that is never sold out.')
    city_hall = create_location(town, 'City Hall', 0, -10, 'The political center of town.')
    unity_chapel = create_location(town, 'Unity Chapel', 10, -10, 'The largest church in town. It is made of pale yellow bricks and has a large steeple.')

    # main st paths
    create_path(grubbers, wild_kingdom)
    create_path(wild_kingdom, flannel_tastic)
    create_path(flannel_tastic, forgotten_pages)
    create_path(forgotten_pages, big_jim_pizza)
    create_path(big_jim_pizza, library)
    create_path(library, iced_creams)
    
    # 100 s paths
    create_path(curiosity_corner, astral_aura)
    create_path(astral_aura, second_chances)
    create_path(second_chances, stockton_bank)
    create_path(stockton_bank, cineplex)
    create_path(cineplex, city_hall)
    create_path(city_hall, unity_chapel)

    # cross-street paths
    create_path(grubbers, curiosity_corner)
    create_path(wild_kingdom, astral_aura)
    create_path(flannel_tastic, second_chances)
    create_path(forgotten_pages, stockton_bank)
    create_path(big_jim_pizza, cineplex)
    create_path(library, city_hall)

    # center street
    highway_39 = create_location(town, 'Highway 39', 0, 120, 'A highway that leads to Turtle Mountain.')
    game_haven = create_location(town, 'Game Haven', 0, 90, 'A game store that deals in card, board, and video games.')
    speedy_mart = create_location(town, 'Speedy Mart', 0, 80, 'A seedy convenience store with a single, run-down gas pump outside.')
    trendsetter_emporium = create_location(town, 'Trendsetter Emporium', 0, 70, 'A high-class fashion store.')
    high_school = create_location(town, 'High School', 0, 40, 'The town high school.')
    city_park = create_location(town, 'City Park', 0, 10, 'The city park, just north of the library.')
    market_masters = create_location(town, 'Market Masters', 0, -20, 'An advertising startup that has grown rapidly in recent years.')

    create_path(game_haven, speedy_mart)
    create_path(speedy_mart, trendsetter_emporium)
    create_path(trendsetter_emporium, city_park)
    create_path(city_park, library)
    create_path(library, market_masters)

    # where players live
    apartments = create_location(town, "Apartment Complex", -30, 30)
    create_path(apartments, library)
    create_path(apartments, city_park)
    create_path(apartments, high_school)

    # Create mountain area and link to town
    turtle_mountain = Area.objects.create(name='Turtle Mountain', meters_per_unit=1000)
    trailhead = create_location(turtle_mountain, 'Turtle Mountain Trailhead', 0, 0)
    water_treatment_plant = create_location(turtle_mountain, 'Water Treatment Plant', 0.25, 0.4)
    turtle_switchbacks = create_location(turtle_mountain, 'Switchbacks', 0.5, 0.5)
    turtle_falls = create_location(turtle_mountain, 'Turtle Falls', 1.25, 0.75)
    turtle_summit = create_location(turtle_mountain, 'Turtle Summit', 2, 0.8)
    turtle_cave = create_location(turtle_mountain, 'Turtle Cave', 2.5, 0.75)
    secret_bunker_entrance = create_location(turtle_mountain, 'Secret Bunker', 2.5, 0.75) # TODO: turn this into a path
    
    create_path(highway_39, trailhead)
    create_path(trailhead, water_treatment_plant)
    create_path(water_treatment_plant, turtle_switchbacks)
    create_path(turtle_switchbacks, turtle_falls)
    create_path(turtle_falls, turtle_summit)
    create_path(turtle_summit, turtle_cave)
    create_path(turtle_cave, secret_bunker_entrance)

    
    create_character_prefab(
        name="Grubby",
        description="The owner of Grubster's Diner. Works long hours and is always willing to talk.",
        appearance="A large middle-aged man with a grease-stained apron and hair net",
        personality="Seems grumpy at first but quickly warms up to you. Very hardworking and focused.",
    )

    create_character_prefab(
        name="Lazuli",
        description="She runs a small spirituality & gemstone shop called Astral Aura. She doesn't do it for the money, she just likes helping others connect with nature and spirituality.",
        appearance="Young woman with blue hair with a dreamy, slighly dazed look on her face.",
        personality="She is an aquarius: detatched, head in the clouds, nature-loving, mystic, natural type person.",
    )

    create_character_prefab(
        name="Ray",
        description="Co-owner of Forgotten Pages, along with his wife Celeste.",
        appearance="A tall, slender middle-aged man dressed in a flashy red suit.",
        personality="Loves books, theater, and drama. Speaks boisterously and in a dramatic fashion.",
    )

    create_character_prefab(
        name="Celeste",
        description="Co-owner of Forgotten pages, along with her husband Ray.",
        appearance="A tall middle-aged librarian woman with glasses with white-blonde hair, wearing a silvery-blue dress.",
        personality="Extravagant, bookish woman who is extremely nice in a very dramatic way.",
    )

    create_character_prefab(
        name="Raul",
        description="The owner of Wild Kingdom, a pet shop infamous for its chaotic environment. People often visit the store not for the animals, but to watch the owner's antics.",
        appearance="A short Spanish man with messy black hair and a bit of stubble.",
        personality="Scatterbrained, energetic, hilariously ADHD and thrill-seeking. Enjoys demonstrating wacky facts about animals (even if those facts are made up).",
    )

    # create_character_prefab(
    #     name="Josh",
    #     appearance="Blond hair",
    #     personality="A total jerk",
    #     description="The game dev",
    #     npc=False,
    # )

seed_database()