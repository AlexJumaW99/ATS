from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Any request to the root URL will be handled by our landing app's urls
    path('', include('landing.urls')),
    # Add the parser app's urls
    path('parser/', include('parser.urls')),
]