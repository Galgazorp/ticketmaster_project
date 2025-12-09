from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ticketmaster_app.urls')),
    path('accounts/', include('accounts.urls')),  # ADD THIS LINE for authentication
]