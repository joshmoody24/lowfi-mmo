from django import forms
from django.forms import ModelForm
from game import models

class WorldForm(ModelForm):
    class Meta:
        model = models.World
        fields = ["name"]
        labels = {
            "name": "World Name",
        }

class CharacterForm(ModelForm):
    class Meta:
        model = models.Character
        fields = "__all__"
        exclude = ["world", "user", "slug", "position", "carry_limit"]
        labels = {
            "name": "Character Name",
        }