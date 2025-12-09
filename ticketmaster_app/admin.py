from django.contrib import admin
from .models import SavedEvent, SearchHistory

@admin.register(SavedEvent)
class SavedEventAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'venue_city', 'event_date', 'saved_at')
    search_fields = ('event_name', 'venue_name')

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('classification', 'city', 'results_count', 'searched_at')