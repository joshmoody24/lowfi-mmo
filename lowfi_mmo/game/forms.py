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
    name = forms.CharField(label="Character Name")

    class Meta:
        model = models.Character
        fields = ["name", "appearance", "personality", "description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add the "name" field back to the form, but use TextInput widget
        self.fields["name"].widget = forms.TextInput(attrs={'placeholder': 'Enter character name'})
        self.fields["appearance"].widget.attrs['placeholder'] = "Tall, dark, handsome male teenager"
        self.fields["personality"].widget.attrs['placeholder'] = "Intelligent, agreeable, and friendly"
        self.fields["description"].widget.attrs['placeholder'] = "Has a girlfriend who goes to a different school. Loves tacos. Flunked second grade"
        for field in ["appearance", "personality", "description"]:
            self.fields[field].widget.attrs['required'] = True
            self.fields[field].widget.attrs['rows'] = 5