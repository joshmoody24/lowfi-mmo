from django.contrib import admin
from game import models

admin.site.register(models.Map)
admin.site.register(models.Location)
admin.site.register(models.LocationConnection)

admin.site.register(models.Species)
admin.site.register(models.Character)
admin.site.register(models.Item)
admin.site.register(models.ItemInstance)