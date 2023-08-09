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
    Command('take', r"^(?:take|t) ([a-zA-Z\ ]*)$", "[item]", "Pick up a nearby item"),
    Command('use', r"^^(?:use|u) \"?([a-zA-Z\ ]*)\"? on \"?([a-zA-Z\ ]*)\"?$", "[item] on [entity]", "Use an item on something"),
]

# TODO: add the following commands
# search (for locations and items tagged hidden)
# clear (clear logs)
# inventory (show carried items)
# help (display help modal)
# exit (route to world details)
# text <group|name> message
# tell/ask/talk to or something
# drop <item>

@atomic
def handle_command(character, raw_input):
    command, args = parse_command(character, raw_input)
    result: systems.Result
    match command:
        case 'go':
            result = systems.move(character, args[0], args[1])
        case 'look':
            result = systems.look(character)
        case 'take':
            result = systems.take(character, args[0])
        case 'use':
            result = systems.use(character, args[0], args[1])
        case _:
            result = systems.Result.fail(f'"{raw_input}" is not a valid command.')
    
    models.CharacterLog.objects.create(
        character=character,
        command=raw_input,
        success=result.success,
        message=result.message
        )
    
def parse_command(character, raw_input):
    for command in COMMANDS:
        match = re.match(command.regex, raw_input.strip().replace("'", ""), re.IGNORECASE)
        if match:
            return command.name.lower(), match.groups()
    return None, None