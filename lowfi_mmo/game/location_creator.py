from game import models
from dataclasses import dataclass

@dataclass
class Location:
    name: str
    interior: True
    appearance: str = ""
    description: str = ""

@dataclass
class TwoWayPath:
    start: str
    end: str
    name: str
    reverse_name: str
    travel_seconds: float = 10.0

@dataclass
class OneWayPath:
    start: str
    end: str
    name: str
    travel_seconds: float = 10.0

@dataclass
class Block:
    start: str
    end: str
    name: str
    appearance: str = ""
    description: str = ""

@dataclass
class Key:
    unlocks: str
    unlock_description: str

locations = [
    # Ruined Mansion
    Location("Ruined Mansion Entrance", False, "Rural mansion in ruins, broken windows, rotting wood", ""),
    Location("Ruined Mansion Living Room", True, "A decayed, rotting living room with plant overgrowth", ""),
    Location("Secret Bunker", True, "Secret bunker", ""),

    # Library
    Location("Library Front Lawn", False, "Small town library"),

    # High School
    Location("Havenbrook High Entrance", False, "A 1980s rural high school", ""),

    # Mountains
    Location("Havenbrook Peak Trailhead", False, "Mountain hiking trailhead"),
    Location("Old Observatory Entrance", False, "Small abandoned observatory on mountaintop")
]

paths = [
    TwoWayPath("Library Front Lawn", "Ruined Mansion Entrance", "to ruined mansion", "to library"),
    TwoWayPath("Ruined Mansion Entrance", "Ruined Mansion Living Room", "inside", "outside"),
    TwoWayPath("Ruined Mansion Living Room", "Secret Bunker", "through trapdoor", "up ladder"),
    
    TwoWayPath("Library Front Lawn", "Havenbrook High Entrance", "to high school", "to library"),

    TwoWayPath("Library Front Lawn", "Havenbrook Peak Trailhead", "to mountains", "to library"),
    TwoWayPath("Havenbrook Peak Trailhead", "Old Observatory Entrance", "to observatory", "to trailhead")
]

blocks = [
    Block("Ruined Mansion Living Room", "Secret Bunker", "Locked Trapdoor", "A large bronze padlock holds the trapdoor firmly in place. It won't budge.")
]

keys = [
    Key("Locked Trapdoor", "The key is a bit dented, but after some fiddling it slides into the keyhole. The padlock pops open with a satisfying click.")
]

def create_locations(world):
    for location in locations:
       models.Location.objects.create(world=world, name=location.name, interior=location.interior, appearance=location.appearance, description=location.description)
    
    for path in paths:
        start = models.Location.objects.get(name=path.start)
        end = models.Location.objects.get(name=path.end)
        models.Path.objects.create(name=path.name, start=start, end=end, travel_seconds=path.travel_seconds)
        if(isinstance(path, TwoWayPath)):
            models.Path.objects.create(name=path.reverse_name, start=end, end=start, travel_seconds=path.travel_seconds)

    for block in blocks:
        path = models.Path.objects.get(start__name=block.start, end__name=block.end)
        models.Block.objects.create(world=world, name=block.name, path=path, appearance=block.appearance, description=block.appearance)

    for key in keys:
        block = models.Block.objects.get(name=key.unlocks)
        models.Key.objects.create(world=world, unlocks=block, unlock_description=key.unlock_description)