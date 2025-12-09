from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_events, name='search_events'),
    path('saved/', views.saved_events, name='saved_events'),
    path('save/<str:event_id>/', views.save_event, name='save_event'),
    path('save-ajax/', views.save_event_ajax, name='save_event_ajax'),
    path('delete/<str:event_id>/', views.delete_saved_event, name='delete_saved_event'),
    path('edit/<str:event_id>/', views.edit_saved_event, name='edit_saved_event'),
]