from django.urls import path
from . import views

app_name = 'space_data'

urlpatterns = [
    path('rocket-families/', views.rocket_family_list, name='rocket_family_list'),
    path('rocket-configurations/', views.rocket_config_list, name='rocket_config_list'),
    path('companies/', views.company_list, name='company_list'),
    path('launch-pads/', views.launch_pad_list, name='launch_pad_list'),
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicle-recovery-methods/', views.vehicle_recovery_method_list, name='vehicle_recovery_method_list'),
    path('payload-groups/', views.payload_group_list, name='payload_group_list'),
    path('launch-missions/', views.launch_mission_list, name='launch_mission_list'),
    path('map/', views.map_view, name='map_view'),
    path('launches/', views.launch_cards, name='launch_cards'),
    path('launch-info/<slug:slug>/', views.launch_detail, name='launch_detail'),
]



