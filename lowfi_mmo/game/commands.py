import re
from game import systems, models

commands = {
    'move': r"^go ([a-zA-Z\ ]*)$",
    'attack': r"^attack ([a-zA-Z\ ]*)$", # r"^attack ([a-zA-Z\ ]*) with ([a-zA-Z\ ]*)$"
    'look': r"^look$",
}

def handle_command(character, raw_input):
    command, variable = parse_command(character, raw_input)
    result = None, None
    if(command == 'move'):
        result =  systems.move(character, variable)
    elif(command == 'attack'):
        result = systems.attack(character, variable)
    elif(command == 'look'):
        result = systems.look(character)
    else:
        result = "", f'"{raw_input}" is not a valid command.'
    
    success = result[0] != "" and result[1] == ""
    print(result)
    print("creating log. Success:", success)
    models.CharacterLog.objects.create(
        character=character,
        command=raw_input,
        success=success,
        result=result[0] if success else result[1]
        )
    
def parse_command(character, raw_input):
    for command, regex in commands.items():
        match = re.match(regex, raw_input, re.IGNORECASE)
        if match:
            return command.lower(), match.group(1).strip()
    return None, None