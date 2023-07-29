from django.contrib import admin
from django.forms import TextInput, Textarea
from game import models
import django.db.models as django_models

class CollapsibleTabularInline(admin.TabularInline):
    classes = ["collapse"]

class WorldMemberInline(CollapsibleTabularInline):
    model = models.WorldMember

class WorldAdmin(admin.ModelAdmin):
    model = models.World
    inlines = [WorldMemberInline]
    search_fields = ["name"]

class LocationInline(CollapsibleTabularInline):
    model = models.Location
    formfield_overrides = {django_models.TextField: {'widget': Textarea(attrs={'rows':1, 'cols':40})}}

class StartPathInline(CollapsibleTabularInline):
    model = models.Path
    autocomplete_fields = ["end"]
    fk_name = "start"
    verbose_name_plural = "Paths that start here"

class EndPathInline(CollapsibleTabularInline):
    model = models.Path
    autocomplete_fields = ["start"]
    fk_name = "end"
    verbose_name_plural = "Paths that lead here"
    
class LocationAdmin(admin.ModelAdmin):
    inlines = [StartPathInline, EndPathInline]
    search_fields = ["name", "description"]
    list_filter = ["category"]
    list_display = ["name", "category"]
    list_editable = ["category"]
    list_display_links = ["name"]

# class CharacterAdmin(admin.ModelAdmin):
#     model = models.Character
#     fieldsets = [
#         (None, {"fields": ["world", "name", "description", "appearance", "personality"]}),
#         ("Advanced options", {"fields": ["carry_limit"], "classes": ["collapse"]})
#     ]
    
admin.site.register(models.World, WorldAdmin)
admin.site.register(models.Location, LocationAdmin)
admin.site.register(models.Character)
admin.site.register(models.Item)
admin.site.register(models.Block)
admin.site.register(models.Name)