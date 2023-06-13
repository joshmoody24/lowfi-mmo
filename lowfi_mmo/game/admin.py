from django.contrib import admin
from game import models

admin.site.register(models.World)
admin.site.register(models.WorldMember)
admin.site.register(models.Area)
admin.site.register(models.Location)
admin.site.register(models.Path)
admin.site.register(models.Species)
admin.site.register(models.Item)
admin.site.register(models.Entity)
admin.site.register(models.Character)
admin.site.register(models.CharacterKnowledge)
admin.site.register(models.Killable)
admin.site.register(models.MagicWielder)
admin.site.register(models.Traveler)
admin.site.register(models.Inventory)
admin.site.register(models.Readable)
admin.site.register(models.ItemInstance)