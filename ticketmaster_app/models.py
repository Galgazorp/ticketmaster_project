from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class SavedEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_events')
    event_id = models.CharField(max_length=100)
    event_name = models.CharField(max_length=255)
    event_url = models.URLField()
    event_image_url = models.URLField(blank=True, null=True)
    venue_name = models.CharField(max_length=255, blank=True, null=True)
    venue_address = models.CharField(max_length=255, blank=True, null=True)
    venue_city = models.CharField(max_length=100, blank=True, null=True)
    venue_state = models.CharField(max_length=50, blank=True, null=True)
    event_date = models.CharField(max_length=100, blank=True, null=True)
    event_time = models.CharField(max_length=50, blank=True, null=True)
    classification = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, default='')
    saved_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-saved_at']
        unique_together = ['user', 'event_id']

    def __str__(self):
        return f"{self.user.username} - {self.event_name} - {self.event_date}"


class SearchHistory(models.Model):
    classification = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    results_count = models.IntegerField(default=0)
    searched_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-searched_at']

    def __str__(self):
        return f"{self.classification} in {self.city}"