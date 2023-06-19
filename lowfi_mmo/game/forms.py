from django.forms import ModelForm
from game import models

from django import forms
from django.utils.html import format_html

from django import forms
from django.utils.html import format_html

class WorldForm(ModelForm):
    class Meta:
        model = models.World
        fields = ["name"]

class CharacterForm(ModelForm):
    location = forms.ModelChoiceField(queryset=models.Location.objects.none())
    def __init__(self, map=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if(map is not None):
            self.fields['location'].queryset = models.Location.objects.filter(map=map)
    class Meta:
        model = models.Character
        fields = "__all__"
        exclude = ["user"]