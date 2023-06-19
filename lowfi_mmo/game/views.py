from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseNotFound
from game import models, forms
from .commands import handle_command
from django.db.models import Subquery

def index(request):
    return render(request, "index.html")

@login_required
def play(request, world_id, character_id):

    character = models.Player.objects.get(entity__world__id=world_id, entity__id=character_id)

    command_result = ""
    error = ""

    if(request.method=="POST"):
        command = request.POST.get('command')
        command_result, error = handle_command(character, command)

    position = models.Position.objects.get(entity=character.entity)
    paths = models.Path.objects.filter(start=position.location)
    entity_ids = models.Position.objects.filter(location=position.location).values('entity_id')
    nearby_npcs = models.Npc.objects.filter(entity_id__in=Subquery(entity_ids))
    nearby_players = models.Player.objects.filter(entity_id__in=Subquery(entity_ids)).exclude(id=character.id)

    context = {
        "player_character": character,
        "hp": models.Health.objects.filter(entity=character.entity).first(),
        "location": position.location,
        "nearby_npcs": nearby_npcs,
        "nearby_players": nearby_players,
        "paths": paths,
        'message': command_result if command_result else None,
        "error": error if error else None,
    }
    return render(request, "play.html", context)

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
def world_create(request):
    if(request.method=="POST"):
        world_form = forms.WorldForm(request.POST)
        if(world_form.is_valid()):
            world_form.instance.user = request.user
            world_form.save()
            return redirect("world_list")
    else:
        world_form = forms.WorldForm()
    context = {
        "form": world_form,
        "form_heading": "Create World",
        "form_submit": "Create World",
    }
    return render(request, "form.html", context)

@login_required
def world_copy(request):
    if(request.method=="POST"):
        form = forms.WorldCopyForm(request.POST)
        if(form.is_valid()):
            from game.game_management import copy_world
            copy_world(form.cleaned_data['world'], form.cleaned_data["name"], request.user)
            return redirect("world_list")
    else:
        form = forms.WorldCopyForm()
    context = {
        "form": form,
        "form_heading": "Create World From Template",
        "form_submit": "Create World",
    }
    return render(request, "form.html", context)

@login_required
def world_details(request, world_id):
    world = get_object_or_404(models.World, id=world_id)
    if(not world.worldmember_set.filter(user=request.user) and not world.owner == request.user):
        return HttpResponseNotFound("World not found.")
    
    # imperative due to locaftion hierarchy. Could improve if this becomes bottleneck
    player_character = models.Player.objects.get(user=request.user)
    print(player_character.entity.id)
    
    context = {
        "world": world,
        "player_character": player_character,
    }
    return render(request, "worlds/world_details.html", context)

@login_required
def world_delete(request, world_id):
    world = get_object_or_404(models.World, id=world_id)
    if(world.owner != request.user):
        return HttpResponseForbidden("You are not allowed to delete this world.")
    if(request.method=="DELETE"):
        world.delete()
        return redirect("world_list")
    
    context = {
        "form_heading": f"Delete Confirmation",
        "form_subheading": f"Are you sure you want to delete {world}?",
        "form_submit": "Yes, I'm sure"
    }
    return render(request, "forms.py", context)

@login_required
def character_list(request):
    user_characters = models.Player.objects.filter(user=request.user)
    return render(request, "characteers/character_select.html", {"user_characters": user_characters})

@login_required
def character_create(request, world_id):
    world = get_object_or_404(models.World, id=world_id)
    if(request.method=="POST"):
        form = forms.CharacterForm(request.POST, map=world.map)
        if(form.is_valid()):
            form.instance.user = request.user
            form.save()
            return redirect("characters/")
    else:
        form = forms.CharacterForm(map=world.map)
    context = {
        "form": form,
        "form_heading": f"Create character in {world}",
        "form_submit": "Create Character",
    }
    return render(request, "form.html", context)

def example(request):
    return render(request, "pico_example.html")