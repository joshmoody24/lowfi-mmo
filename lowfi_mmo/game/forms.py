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

class PlayerInstanceForm(ModelForm):
    location = forms.ModelChoiceField(queryset=models.Location.objects.all())
    ''' limit spawn points to area
    def __init__(self, area=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if(area is not None):
            self.fields['location'].queryset = models.Location.objects.filter(area=area)
    '''
    class Meta:
        model = models.PlayerInstance
        fields = "__all__"
        exclude = ["user", "world", "base"]

class PlayerForm(ModelForm):
    class Meta:
        model = models.Player
        fields = "__all__"