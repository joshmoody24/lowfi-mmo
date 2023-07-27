import re
from game import systems

commands = {
    'move': r"^go ([a-zA-Z\ ]*)$",
    'attack': r"^attack ([a-zA-Z\ ]*)$" # r"^attack ([a-zA-Z\ ]*) with ([a-zA-Z\ ]*)$"
}

def handle_command(character, raw_input):
    command, variable = parse_command(character, raw_input)
    if(command == 'move'):
        return systems.move(character, variable)
    elif(command == 'attack'):
        return systems.attack(character, variable)
    else:
        return "", f'"{raw_input}" is not a valid command.'

def parse_command(character, raw_input):
    for command, regex in commands.items():
        match = re.match(regex, raw_input, re.IGNORECASE)
        if match:
            return command.lower(), match.group(1).strip()
    return None, None