import re
from game import systems

commands = {
    'move': r"^go to ([a-zA-Z\ ]*)$",
    'attack': r"^attack ([a-zA-Z\ ]*)$" # r"^attack ([a-zA-Z\ ]*) with ([a-zA-Z\ ]*)$"
}

def handle_command(character, raw_input):
    command, variable = parse_command(character, raw_input)
    if command is None:
        return "", "Command not recognized"
    if(command.lower() == 'move'):
        return systems.move(character.entity, variable)
    elif(command.lower() == 'attack'):
        return systems.attack(character.entity, variable)
    else:
        return "", "Command not recognized."

def parse_command(character, raw_input):
    for command, regex in commands.items():
        match = re.match(regex, raw_input, re.IGNORECASE)
        if match:
            return command, match.group(1).strip()
    return None, None