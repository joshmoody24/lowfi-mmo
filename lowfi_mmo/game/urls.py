from django.urls import path
from game import views

urlpatterns = [
    path('', views.index, name='index'),

    # worlds
    path('worlds/', views.world_list, name='world_list'),
    path('worlds/details/<int:world_id>', views.world_details, name='world_details'),
    path('worlds/create/', views.world_create, name='world_create'),
    path('worlds/delete/<int:world_id>', views.world_delete, name='world_delete'),
    path('worlds/edit/<int:world_id>', views.world_edit, name='world_edit'),

    # characters
    path('characters/', views.character_list, name='character_list'),
    path('worlds/<int:world_id>/characters/create/', views.character_create, name='character_create'),
    path('worlds/<int:world_id>/characters/edit/<slug:character_slug>/', views.character_edit, name="character_edit"),
    path('play/<int:world_id>/<slug:character_slug>/', views.play, name='play'),

    # other
    path('areas/<int:area_id>/map/', views.area_map, name='location_map')
]