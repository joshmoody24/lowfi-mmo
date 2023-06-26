from django.contrib import admin
from django.forms import TextInput, Textarea
from game import models
import django.db.models as django_models
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.models import ContentType

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

class AreaAdmin(admin.ModelAdmin):
    inlines = [LocationInline]
    search_fields = ["name"]

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

class ItemInstanceInline(CollapsibleTabularInline):
    model = models.DroppedItem
    autocomplete_fields = ['item', 'location']
    
class LocationAdmin(admin.ModelAdmin):
    inlines = [StartPathInline, EndPathInline, ItemInstanceInline]
    search_fields = ["name", "description"]
    list_filter = ["area"]

class InventoryItemInline(CollapsibleTabularInline):
    model = models.InventoryItem
    autocomplete_fields = ["item"]

class PlayerInstanceInline(admin.StackedInline):
    model = models.PlayerInstance

class PlayerAdmin(admin.ModelAdmin):
    inlines = [PlayerInstanceInline]

class NpcPrefabAdmin(admin.ModelAdmin):
    model = models.NpcPrefab
    fieldsets = [
        (None, {"fields": ["name", "gender", "description", "appearance", "personality"]}),
        ("Advanced options", {"fields": ["carry_limit"], "classes": ["collapse"]})
    ]

class CharacterAdmin(admin.ModelAdmin):
    inlines = [InventoryItemInline]
    search_fields = ["traits__name", "traits__appearance", "traits__personality"]
    autocomplete_fields = ["world", "location"]

class ConversationParticipantInline(CollapsibleTabularInline):
    model = models.ConversationParticipant
    autocomplete_fields = ["character"]

class ConversationAdmin(admin.ModelAdmin):
    inlines = [ConversationParticipantInline]
    autocomplete_fields = ["setting"]

# class FromTopicConnectionInline(CollapsibleTabularInline):
#     model = models.TopicConnection
#     fk_name = "from_topic"

# class ToTopicConnectionInline(CollapsibleTabularInline):
#     model = models.TopicConnection
#     fk_name = "to_topic"

# class ContextInline(GenericTabularInline):
#     model = models.TopicContext
#     ct_field = "context_type"
#     ct_fk_field = "context_object_id"
#     extra = 1
#     # formfield_overrides = {django_models.TextField: {'widget': Textarea(attrs={'rows':3, 'cols':40})}}

# class TopicAdmin(admin.ModelAdmin):
#     inlines = [
#         ContextInline,
#         FromTopicConnectionInline,
#         ToTopicConnectionInline,
#     ]

class ItemAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["name", "description", "weight_kg", "value"]}),
        ("Advanced options", {"fields": ["readable_message"], "classes": ["collapse"]})
    ]
    search_fields = ["name", "description", "readable_message"]

class ItemInstanceAdmin(admin.ModelAdmin):
    autocomplete_fields = ["item", "location"]
    
# base models

admin.site.register(models.World, WorldAdmin)
admin.site.register(models.Area, AreaAdmin)
admin.site.register(models.Location, LocationAdmin)
admin.site.register(models.ItemPrefab, ItemAdmin)
admin.site.register(models.DroppedItem, ItemInstanceAdmin)
admin.site.register(models.NpcPrefab, NpcPrefabAdmin)
admin.site.register(models.Player, PlayerAdmin)
admin.site.register(models.NpcInstance)

# conversation models

# admin.site.register(models.Conversation, ConversationAdmin)
# admin.site.register(models.Topic, TopicAdmin)