from django.contrib import admin
from game import models

class WorldMemberInline(admin.TabularInline):
    model = models.WorldMember

class WorldAdmin(admin.ModelAdmin):
    model = models.World
    inlines = [WorldMemberInline]

class LocationInline(admin.TabularInline):
    model = models.Location

class AreaAdmin(admin.ModelAdmin):
    inlines = [LocationInline]

class StartPathAdmin(admin.TabularInline):
    model = models.Path
    fk_name = "start"

class EndPathAdmin(admin.TabularInline):
    model = models.Path
    fk_name = "end"

class ItemInstanceInline(admin.TabularInline):
    model = models.ItemInstance
    
class LocationAdmin(admin.ModelAdmin):
    inlines = [StartPathAdmin, EndPathAdmin, ItemInstanceInline]

class PlayerInline(admin.StackedInline):
    model = models.Player

class NpcInline(admin.StackedInline):
    model = models.Npc


class InventoryItemInline(admin.TabularInline):
    model = models.InventoryItem

class CharacterAdmin(admin.ModelAdmin):
    inlines = [InventoryItemInline]

admin.site.register(models.World, WorldAdmin)
admin.site.register(models.Area, AreaAdmin)
admin.site.register(models.Location, LocationAdmin)
admin.site.register(models.Player, CharacterAdmin)
admin.site.register(models.Npc, CharacterAdmin)
admin.site.register(models.Item)
admin.site.register(models.ItemInstance)