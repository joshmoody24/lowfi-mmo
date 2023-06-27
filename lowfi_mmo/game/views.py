from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseNotFound
from game import models, forms
from .commands import handle_command
from django.db.models import Subquery
from django.db import transaction
import plotly.graph_objects as go
from io import BytesIO
from django.http import HttpResponse

def index(request):
    return render(request, "index.html")

@login_required
def play(request, world_id, character_id):

    player = models.PlayerInstance.objects.get(world__id=world_id, id=character_id)

    command_result = ""
    error = ""

    if(request.method=="POST"):
        command = request.POST.get('command')
        command_result, error = handle_command(player, command)

    paths = models.Path.objects.filter(start=player.location)
    nearby_npcs = models.NpcInstance.objects.filter(location=player.location)
    nearby_players = models.PlayerInstance.objects.filter(location=player.location)

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
            # spawn in the NPCs
            # TODO: flesh out the spawn point system
            for npc in models.NpcPrefab.objects.all():
                spawn_point = npc.owned_locations.first() if npc.owned_locations.count() > 0 else models.Location.objects.get(name__iexact="library")
                models.NpcInstance.objects.create(prefab=npc, world=world, location=spawn_point)
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
    
    player_character = models.PlayerInstance.objects.filter(user=request.user).first()
    
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
        models.Player.objects.filter(world=world).delete()
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
    user_characters = models.PlayerInstance.objects.filter(user=request.user)
    return render(request, "characteers/character_select.html", {"user_characters": user_characters})

@login_required
@transaction.atomic
def character_create(request, world_id):
    world = get_object_or_404(models.World, id=world_id)
    if(request.method=="POST"):
        player_instance_form = forms.PlayerInstanceForm(request.POST)
        player_form = forms.PlayerForm(request.POST)
        if(player_instance_form.is_valid() and player_form.is_valid()):
            player_instance_form.instance.user = request.user
            player_instance_form.instance.world_id = world_id
            instance = player_instance_form.save()
            player_form.instance.instance_id = instance.id
            player_form.save()
            return redirect("world_details", world_id=world_id)
    else:
        player_instance_form = forms.PlayerInstanceForm()
        player_form = forms.PlayerForm()
    context = {
        "form": player_form,
        "related_form": player_instance_form,
        "form_heading": f"Create character in {world}",
        "form_submit": "Create Character",
    }
    return render(request, "form.html", context)


def area_map(request, area_id):
    # Fetch all instances of the Location model
    area = get_object_or_404(models.Area, id=area_id)
    kilometers_per_unit = area.meters_per_unit / 1000
    locations = models.Location.objects.filter(area_id=area_id)
    
    # Extract x, y, and name values from each location
    x_values = [location.x for location in locations]
    y_values = [location.y for location in locations]
    names = [location.name for location in locations]
    types = [location.location_type for location in locations]
    
    # Map location types to colors
    color_mapping = {'store': 'red', 'house': 'green'}
    colors = [color_mapping.get(location_type, 'blue') for location_type in types]
    
    # Convert x and y values to kilometers
    x_values = [x * kilometers_per_unit for x in x_values]
    y_values = [y * kilometers_per_unit for y in y_values]

    # Fetch all instances of the Path model
    paths = models.Path.objects.filter(start__area_id=area_id, end__area_id=area_id)
    
    # Extract start and end locations for each path
    start_locations = [path.start for path in paths]
    end_locations = [path.end for path in paths]
    
    # Convert start and end locations to indices
    start_indices = [names.index(start.name) for start in start_locations]
    end_indices = [names.index(end.name) for end in end_locations]
    
    # Create a scatter plot of the locations using Plotly
    fig = go.Figure(data=go.Scatter(x=x_values, y=y_values, mode='markers', marker=dict(color=colors)))
    
    # Add labels for each point
    for i, name in enumerate(names):
        fig.add_annotation(
            x=x_values[i],
            y=y_values[i],
            text=name,
            showarrow=False,
            # font=dict(size=8),
            xanchor='center',
            yanchor='top',
            # yshift=-10
        )
    
    # Add lines between start and end locations
    for start_idx, end_idx in zip(start_indices, end_indices):
        fig.add_trace(go.Scatter(
            x=[x_values[start_idx], x_values[end_idx]],
            y=[y_values[start_idx], y_values[end_idx]],
            mode='lines',
            line=dict(color='rgba(128, 128, 128, 0.5)', width=1),
            showlegend=False
        ))

    # Set axes labels and title
    fig.update_layout(
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        title= area.name
    )
    
    # Convert the figure to HTML
    plot_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    # Create the HTTP response with the plot HTML
    response = HttpResponse(content_type='text/html')
    response.write(plot_html)
    
    return response