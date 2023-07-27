from django import forms
from django.forms import ModelForm
from game import models

class WorldForm(ModelForm):
    class Meta:
        model = models.World
        fields = ["name"]

class CharacterForm(ModelForm):
    class Meta:
        model = models.Character
        fields = "__all__"
        exclude = ["world", "user", "slug"]