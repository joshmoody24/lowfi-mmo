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
class OneWayBlock:
    start: str
    end: str
    name: str
    appearance: str = ""
    description: str = ""

class TwoWayBlock(OneWayBlock):
    pass

@dataclass
class Key:
    name: str
    description: str
    appearance: str
    position: str
    unlocks: str
    unlock_description: str


locations = [
    # Ruined Mansion
    Location("Ruined Mansion Entrance", False, "Rural mansion in ruins, broken windows, rotting wood", "An eerie entrance to a crumbling mansion."),
    Location("Ruined Mansion Living Room", True, "A decayed, rotting living room with plant overgrowth", "A once-grand living room now consumed by nature."),
    Location("Secret Bunker", True, "Secret bunker", "A hidden underground bunker filled with mysterious treasures."),

    # Library
    Location("Library Front Lawn", False, "Small town library", "The serene front lawn of a quaint little library."),

    # High School
    Location("Havenbrook High Entrance", False, "A 1980s rural high school", "The entrance of an old rural high school."),

    # Pawn Shop
    Location("Curiosity Corner", True, "Pawn shop exterior", "An old pawn shop in the middle of town."),

    # Mountains
    Location("Havenbrook Peak Trailhead", False, "Mountain hiking trailhead", "The starting point of a scenic mountain hiking trail."),
    Location("Old Observatory Entrance", False, "Small abandoned observatory on mountaintop", "An abandoned observatory atop the mountains, offering panoramic views.")
]

paths = [
    TwoWayPath("Library Front Lawn", "Ruined Mansion Entrance", "to ruined mansion", "to library"),
    TwoWayPath("Ruined Mansion Entrance", "Ruined Mansion Living Room", "inside", "outside"),
    TwoWayPath("Ruined Mansion Living Room", "Secret Bunker", "through trapdoor", "up ladder"),
    
    TwoWayPath("Library Front Lawn", "Havenbrook High Entrance", "to high school", "to library"),

    TwoWayPath("Library Front Lawn", "Curiosity Corner", "to pawn shop", "to library"),

    TwoWayPath("Library Front Lawn", "Havenbrook Peak Trailhead", "to mountains", "to library"),
    TwoWayPath("Havenbrook Peak Trailhead", "Old Observatory Entrance", "to observatory", "to trailhead")
]

blocks = [
    TwoWayBlock("Ruined Mansion Living Room", "Secret Bunker", "Trapdoor", "A large bronze padlock holds the trapdoor firmly in place. It won't budge.", "A hidden trapdoor leading to the secret bunker.")
]

keys = [
    Key("Bronze Key", "An old fashioned bronze key with a few dents.", "An old fashioned bronze key with a few dents.", "Curiosity Corner", "Locked Trapdoor", "The key is a bit dented, but after some fiddling, it slides into the keyhole. The padlock pops open with a satisfying click.")
]

def create_locations(world):
    for location in locations:
       models.Location.objects.create(world=world, name=location.name, interior=location.interior, appearance=location.appearance, description=location.description)
    
    for path in paths:
        start = models.Location.objects.get(world=world, name=path.start)
        end = models.Location.objects.get(world=world, name=path.end)
        models.Path.objects.create(name=path.name, start=start, end=end, travel_seconds=path.travel_seconds)
        if(isinstance(path, TwoWayPath)):
            models.Path.objects.create(name=path.reverse_name, start=end, end=start, travel_seconds=path.travel_seconds)

    for block in blocks:
        starts = [block.start] if isinstance(block, OneWayBlock) else [block.start, block.end]
        ends = [block.end] if isinstance(block, OneWayBlock) else [block.start, block.end]
        blocked_paths = models.Path.objects.filter(start__world=world, end__world=world, start__name__in=starts, end__name__in=ends)
        block_obj = models.Block.objects.create(world=world, name=block.name, appearance=block.appearance, description=block.appearance)
        for path in blocked_paths:
            block_obj.paths.add(path)

    for key in keys:
        block = models.Block.objects.get(world=world, name=key.unlocks)
        position = models.Location.objects.get(world=world, name=key.position)
        models.Key.objects.create(world=world, name=key.name, description=key.description, appearance=key.appearance, unlocks=block, unlock_description=key.unlock_description, position=position)