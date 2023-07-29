import re
from game import systems, models
from dataclasses import dataclass
from django.db.transaction import atomic

@dataclass
class Command:
    name: str
    regex: str
    arg_syntax: str
    description: str

COMMANDS = [
    Command('look', r"^(?:look|l)$", "", "Examine your surroundings"),
    Command('go', r"^(?:go|g)(?: (back|to|through|inside|outside))?(?: ([a-zA-Z\ ]*))?$", "[position]", "Follow a path to a new location"),
    Command('take', r"^take ([a-zA-Z\ ]*)$", "[item]", "Pick up a nearby item"),
    Command('use', r"^^use \"?([a-zA-Z\ ]*)\"? on \"?([a-zA-Z\ ]*)\"?$", "[item] on [entity]", "Use an item on something"),
    Command('attack', r"^attack ([a-zA-Z\ ]*)$", "[character]", "Attack a character"), # r"^attack ([a-zA-Z\ ]*) with ([a-zA-Z\ ]*)$"
]

# TODO: add the following commands
# search (for locations and items tagged hidden)
# clear (clear logs)
# inventory (show carried items)
# help (display help modal)
# exit (route to world details)
# text <group|name> message
# tell/ask/talk to or something

@atomic
def handle_command(character, raw_input):
    command, args = parse_command(character, raw_input)
    result = None, None
    if(command == 'go'):
        result =  systems.move(character, args[0], args[1])
    elif(command == 'attack'):
        result = systems.attack(character, args[0])
    elif(command == 'look'):
        result = systems.look(character)
    elif(command == 'take'):
        result = systems.take(character, args[0])
    elif(command == 'use'):
        result = systems.use(character, args[0], args[1])
    else:
        result = "", f'"{raw_input}" is not a valid command.'
    
    success = result[0] != "" and result[1] == ""
    models.CharacterLog.objects.create(
        character=character,
        command=raw_input,
        success=success,
        result=result[0] if success else result[1]
        )
    
def parse_command(character, raw_input):
    for command in COMMANDS:
        match = re.match(command.regex, raw_input.strip(), re.IGNORECASE)
        if match:
            return command.name.lower(), match.groups()
    return None, None