from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseNotFound
from game import models, forms
from .commands import handle_command
from django.db import transaction
from django.http import HttpResponse
from .world_creator import populate_world
from .world_visualizer import world_to_html

def index(request):
    return render(request, "index.html")

@login_required
def play(request, world_id, character_slug):
    player = models.Character.objects.get(world__id=world_id, slug=character_slug, user=request.user)

    command_result = ""
    error = ""

    if(request.method=="POST"):
        command = request.POST.get('command')
        command_result, error = handle_command(player, command)

    paths = models.Path.objects.filter(start=player.position)
    nearby_npcs = models.Character.objects.filter(position=player.position, user=None)
    nearby_players = models.Character.objects.filter(position=player.position).exclude(id=player.id)

    context = {
        "player": player,
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
@transaction.atomic
def world_create(request):
    if(request.method=="POST"):
        world_form = forms.WorldForm(request.POST)
        if(world_form.is_valid()):
            world_form.instance.owner = request.user
            world = world_form.save()
            populate_world(world)
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
def world_details(request, world_id):
    world = get_object_or_404(models.World, id=world_id)
    if(not world.worldmember_set.filter(user=request.user) and not world.owner == request.user):
        return HttpResponseNotFound("World not found.")
    
    player_character = models.Character.objects.filter(user=request.user).first()
    
    context = {
        "world": world,
        "player_character": player_character,
    }
    return render(request, "worlds/world_details.html", context)

@login_required
@transaction.atomic
def world_delete(request, world_id):
    print(request.method)
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
        character_form = forms.CharacterForm(request.POST)
        if(character_form.is_valid()):
            character_form.instance.user = request.user
            character_form.instance.world_id = world_id
            character_form.save()
            return redirect("world_details", world_id=world_id)
    else:
        character_form = forms.CharacterForm()
    context = {
        "form": character_form,
        "form_heading": f"Create character in {world}",
        "form_submit": "Create Character",
    }
    return render(request, "form.html", context)

def character_edit(request, world_id, character_slug):
    character = get_object_or_404(models.Character, world_id=world_id, slug=character_slug, user=request.user)
    if(request.method=="POST"):
        character_form = forms.CharacterForm(request.POST)
        if(character_form.is_valid()):
            character_form.instance.user = request.user
            character_form.instance.world_id = world_id
            character_form.save()
            return redirect("world_details", world_id=world_id)
    else:
        character_form = forms.CharacterForm(instance=character)
    context = {
        "form": character_form,
        "form_heading": f"Edit character in {character.world}",
        "form_submit": "Save Changes",
    }
    return render(request, "form.html", context)


def area_map(request, world_id):
    area = get_object_or_404(models.World, id=world_id)
    plot_html = world_to_html(area)
    response = HttpResponse(content_type='text/html')
    response.write(plot_html)
    return response