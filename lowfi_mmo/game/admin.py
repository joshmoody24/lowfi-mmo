from django.contrib import admin
from game import models

admin.site.register(models.World)
admin.site.register(models.WorldMember)
admin.site.register(models.Area)
admin.site.register(models.Location)
admin.site.register(models.Path)
admin.site.register(models.Item)
admin.site.register(models.Entity)
admin.site.register(models.Player)
admin.site.register(models.Npc)
admin.site.register(models.Health)
admin.site.register(models.Traveler)
admin.site.register(models.Inventory)
admin.site.register(models.Readable)
admin.site.register(models.ItemInstance)