from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseNotFound
from game import models, forms
from .commands import handle_command
from django.db import transaction
from django.http import HttpResponse
from .worldgen.world_creator import populate_world
from .worldgen.world_visualizer import world_to_html
from .commands import COMMANDS
from datetime import datetime

def index(request):
    return render(request, "index.html")

@login_required
def play(request, world_id, character_slug):
    player = models.Character.objects.get(world__id=world_id, names__slug=character_slug, user=request.user)

    if(request.method=="POST"):
        command = request.POST.get('command')
        handle_command(player, command)

    paths = player.position.start_paths.all()
    nearby_npcs = models.Character.objects.filter(position=player.position, user=None)
    nearby_players = models.Character.objects.filter(position=player.position).exclude(id=player.id)
    most_recent_success_log = player.characterlog_set.filter(success=True).order_by('-created_at').first()
    most_recent_error_log = player.characterlog_set.filter(success=False).order_by('-created_at').first()

    MAX_HISTORY = 1
    logs = player.characterlog_set.order_by('-created_at')[:MAX_HISTORY]

    context = {
        "player": player,
        "nearby_npcs": nearby_npcs,
        "nearby_players": nearby_players,
        "paths": paths,
        'success_log': most_recent_success_log,
        'error_log': most_recent_error_log,
        'log_history': logs,
        'commands': COMMANDS,
    }
    return render(request, "play.html", context)

@login_required
def world_list(request):
    owned_worlds = models.World.objects.filter(owner=request.user)
    participant_worlds = models.World.objects.filter(worldmember__user=request.user)
    context = {
        "owned_worlds": owned_worlds,
        "participant_worlds": participant_worlds,
        "world_count": len(owned_worlds) + len(participant_worlds)
    }
    return render(request, "worlds/world_list.html", context)

@login_required
@transaction.atomic
def world_create(request):
    if(request.method=="POST"):
        world_form = forms.WorldForm(request.POST, prefix="world")
        if(world_form.is_valid()):
            world_form.instance.owner = request.user
            world = world_form.save()
            populate_world(world)
            return redirect("world_list")
    else:
        world_form = forms.WorldForm(prefix="world")
    context = {
        "form": world_form,
        "form_heading": "Create World",
        "form_submit": "Create World",
    }
    return render(request, "form.html", context)

@login_required
@transaction.atomic
def world_edit(request, world_id):
    world = get_object_or_404(models.World, id=world_id)
    if(world.owner_id != request.user.id):
        return HttpResponseForbidden("You don't have permissions to edit this world.")
    if(request.method == "POST"):
        world_form = forms.WorldForm(request.POST, instance=world, prefix="world") # prefix to avoid person name autocomplete suggestions
        if(world_form.is_valid()):
            world_form.instance.save()
            return redirect("world_details", world_id=world_id)
    else:
        world_form = forms.WorldForm(instance=world, prefix="world")
    context = {
        "form": world_form,
        "form_heading": "Edit World",
        "form_submit": "Save Changes",
    }
    return render(request, "form.html", context)
    

@login_required
def world_details(request, world_id):
    world = get_object_or_404(models.World, id=world_id)
    if(not world.worldmember_set.filter(user=request.user) and not world.owner == request.user):
        return HttpResponseNotFound("World not found.")
    
    player_character = models.Character.objects.filter(world_id=world_id, user=request.user).first()
    
    context = {
        "world": world,
        "player_character": player_character,
    }
    return render(request, "worlds/world_details.html", context)

@login_required
@transaction.atomic
def world_delete(request, world_id):
    world = get_object_or_404(models.World, id=world_id)
    if(world.owner != request.user):
        return HttpResponseForbidden("You are not allowed to delete this world.")
    if(request.method == "POST"):
        world.delete()
        return redirect("world_list")
    
    context = {
        "form_heading": f"Delete Confirmation",
        "form_subheading": f"Are you sure you want to delete {world}?",
        "form_submit": "Yes, I'm sure",
    }
    return render(request, "form.html", context)

@login_required
def character_list(request):
    user_characters = models.Character.objects.filter(user=request.user)
    return render(request, "characters/character_select.html", {"user_characters": user_characters})

@login_required
@transaction.atomic
def character_create(request, world_id):
    world = get_object_or_404(models.World, id=world_id)
    if(request.method=="POST"):
        character_form = forms.CharacterForm(request.POST, prefix="character") # avoid real person name autocomplete
        if(character_form.is_valid()):
            character_form.instance.user = request.user
            character_form.instance.world_id = world_id
            character_name = character_form.cleaned_data['name']
            HUB_NAME = "apartment complex"
            hub = models.Location.objects.get(world_id=world_id, names__name__iexact=HUB_NAME)
            spawnpoint = models.Location.objects.create(world_id=world_id, appearance="Interior of cheap apartment living room", description=f"A dingy little apartment that isn't worth writing home about. It's alright, you suppose.")
            spawnpoint.names.create(world_id=world_id, name=f"{character_name}'s apartment")
            models.Path.objects.create(preposition="outside", start=spawnpoint, end=hub)
            models.Path.objects.create(preposition="to", noun=f"{character_name}'s apartment", start=hub, end=spawnpoint)
            character_form.instance.position = spawnpoint
            character = character_form.save()
            character.names.create(world_id=world_id, name=character_form.cleaned_data['name'])
            INITIAL_MESSAGE = """You are {name}. You check your phone: {time}. You are chilling in the {location}. You stand up and take a deep breath. You get ready to rumble.
            <br/><br/>
            <span class="tutorial">You can view your surroundings by using the <code>look</code> command.</span>
            <br/><br/>
            <span class="tutorial">Use the <code>[?]</code> button to view gameplay related help.</span>"""
            initial_log = models.CharacterLog.objects.create(
                character=character,
                command="start game",
                message=INITIAL_MESSAGE.format(name=character.name, time=datetime.now().strftime("%I:%M %p").lstrip("0"), location=spawnpoint.name)
            )
            return redirect("world_details", world_id=world_id)
    else:
        character_form = forms.CharacterForm(prefix="character")
    context = {
        "form": character_form,
        "form_heading": f"Create character in {world}",
        "form_submit": "Create Character",
    }
    return render(request, "form.html", context)

def character_edit(request, world_id, character_slug):
    character = get_object_or_404(models.Character, world_id=world_id, names__slug=character_slug, user=request.user)
    if(character.user_id != request.user.id):
        return HttpResponseForbidden("You don't have permissions to edit this character.")
    if(request.method=="POST"):
        character_form = forms.CharacterForm(request.POST, instance=character, prefix="character")
        if(character_form.is_valid()):
            character_form.save()
            name = character_form.cleaned_data['name']
            first_name = character.names.first()
            first_name.name = name
            first_name.save()
            return redirect("world_details", world_id=world_id)
    else:
        character_form = forms.CharacterForm(instance=character, prefix="character", initial={"name": character.name})
    context = {
        "form": character_form,
        "form_heading": "Edit Character",
        "form_subheading": f"{character_form.instance.name} from {character_form.instance.world.name}",
        "form_submit": "Save Changes",
    }
    return render(request, "form.html", context)


def world_visualize(request, world_id):
    area = get_object_or_404(models.World, id=world_id)
    plot_html = world_to_html(area)
    response = HttpResponse(content_type='text/html')
    response.write(plot_html)
    return response