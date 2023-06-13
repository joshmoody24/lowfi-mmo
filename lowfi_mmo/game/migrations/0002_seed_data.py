from django.db import migrations
from django.contrib.auth import get_user_model

def populate_database(apps, schema_editor):
    # Create an initial superuser
    User = apps.get_model('auth', 'User')
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@fake.com', 'password')

    # Access the models using the apps parameter
    World = apps.get_model('game', 'World')
    Area = apps.get_model('game', 'Area')
    Location = apps.get_model('game', 'Location')
    Path = apps.get_model('game', 'Path')
    Species = apps.get_model('game', 'Species')
    Item = apps.get_model('game', 'Item')
    Entity = apps.get_model('game', 'Entity')
    Position = apps.get_model('game', 'Position')
    Killable = apps.get_model('game', 'Killable')
    Inventory = apps.get_model('game', 'Inventory')
    Traveler = apps.get_model('game', 'Traveler')
    Character = apps.get_model('game', 'Character')
    ItemInstance = apps.get_model('game', 'ItemInstance')

    # Create world
    central_earth = World.objects.create(name='Central Earth', owner=User.objects.first())
    
    # Create overworld area
    overworld = Area.objects.create(world=central_earth, name='Overworld', meters_per_unit = 1000)
    
    castle = Location.objects.create(area=overworld, name='Central Earth Castle', x=0, y=0, description='A huge, imposing castle')
    mogus_village = Location.objects.create(area=overworld, name='Mogus Village', x=2, y=1, description='A small village')
    castle_town = Location.objects.create(area=overworld, name='Central Earth Castle Town', x=0, y=-0.5, description='A bustling metropolis just south of Central Earth Castle')
    deathville = Location.objects.create(area=overworld, name='Deathville', x=-1, y=-2, description='A ghost town on the way to Boardoor')
    boardoor = Location.objects.create(area=overworld, name='Boardoor', x=-10, y=-20, description='An evil nation with a big eyeball tower')

    Path.objects.create(start=castle, end=castle_town)
    Path.objects.create(start=castle_town, end=castle)
    Path.objects.create(start=castle_town, end=deathville)
    Path.objects.create(start=deathville, end=castle_town)
    Path.objects.create(start=deathville, end=boardoor)
    Path.objects.create(start=boardoor, end=deathville)
    Path.objects.create(start=castle_town, end=mogus_village)
    Path.objects.create(start=mogus_village, end=castle_town)

    central_earth.spawn_point = mogus_village
    mogus_village.save()

    # Create castle area and link to overworld
    castle_interior = Area.objects.create(world=central_earth, name='Central Earth Castle Interior', meters_per_unit=1)
    entrance = Location.objects.create(area=castle_interior, name='Castle Entrance', x=0, y=0)
    Path.objects.create(start=entrance, end=castle)
    Path.objects.create(start=castle, end=entrance)
    
    armory = Location.objects.create(area=castle_interior, name='Armory', x=50, y=5)
    armory_trash_chute = Location.objects.create(area=castle_interior, name='Armory Trash Chute', x=50, y=0)
    throne_room = Location.objects.create(area=castle_interior, name='Throne Room', x=0, y=100)
    library = Location.objects.create(area=castle_interior, name='Library', x=-50, y=10)
    library_closet = Location.objects.create(area=castle_interior, name='Library Closet', x=-50, y=12)

    Path.objects.create(start=entrance, end=armory)
    Path.objects.create(start=armory, end=entrance)
    Path.objects.create(start=armory, end=armory_trash_chute)
    Path.objects.create(start=entrance, end=throne_room)
    Path.objects.create(start=throne_room, end=entrance)
    Path.objects.create(start=entrance, end=library)
    Path.objects.create(start=library, end=entrance)
    Path.objects.create(start=library, end=library_closet)
    Path.objects.create(start=library_closet, end=library)

    # Create dungeon area and link it to castle
    dungeon = Area.objects.create(world=central_earth, name='Central Earth Castle Dungeon', meters_per_unit=1, elevation=-20)
    trash_pile = Location.objects.create(area=dungeon, name='Trash Pile', x=-50, y=10)
    prison_cells = Location.objects.create(area=dungeon, name='Prison Cells', x=0, y=0)
    Path.objects.create(start=armory_trash_chute, end=trash_pile)
    Path.objects.create(start=throne_room, end=prison_cells, name='Mysterious Trapdoor')
    Path.objects.create(start=prison_cells, end=throne_room)

    execution_chamber = Location.objects.create(area=dungeon, name='Execution Chamber', x=50, y=0)
    evacuation_tunnel = Location.objects.create(area=dungeon, name='Secret Evacuation Tunnel', x=50, y=-100)

    Path.objects.create(start=trash_pile, end=prison_cells)
    Path.objects.create(start=prison_cells, end=trash_pile)
    Path.objects.create(start=prison_cells, end=execution_chamber)
    Path.objects.create(start=execution_chamber, end=prison_cells)
    Path.objects.create(start=execution_chamber, end=evacuation_tunnel)
    Path.objects.create(start=evacuation_tunnel, end=execution_chamber)
    Path.objects.create(start=evacuation_tunnel, end=castle_town)

    # Species
    human = Species.objects.create(world=central_earth, name='Human')
    dwarf = Species.objects.create(world=central_earth, name='Dwarf')
    elf = Species.objects.create(world=central_earth, name='Elf')

    # Items
    broadsword = Item.objects.create(world=central_earth, name='Broadsword', description='A broadsword', attack=4)
    buckler = Item.objects.create(world=central_earth, name='Buckler', description='A simple shield', defense=2)
    apple = Item.objects.create(world=central_earth, name='Apple', description='A tasty snack', healing=1, weight_kg=0.1)

    apple_entity = Entity.objects.create(world=central_earth, name='apple_entity')
    ItemInstance.objects.create(entity=apple_entity, item=apple, dropped_location=trash_pile)

    def create_character(world, name, species, location, player=None):
        entity = Entity.objects.create(world=world, name=name)
        Position.objects.create(entity=entity, location=location)
        Killable.objects.create(entity=entity)
        Character.objects.create(entity=entity, species=species, player=player)
        if(player): # just for simplicity
            Traveler.objects.create(entity=entity)
            inventory = Inventory.objects.create(entity=entity)
            ItemInstance.objects.create(entity=entity, item=broadsword, inventory=inventory)

    create_character(central_earth, "Urist", dwarf, mogus_village, User.objects.first())
    create_character(central_earth, "The Monarch", dwarf, throne_room)
    create_character(central_earth, "Feetless", elf, prison_cells)
    create_character(central_earth, "Carl", human, castle_town)

class Migration(migrations.Migration):
    

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_database),
    ]
