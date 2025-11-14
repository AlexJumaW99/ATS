from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import os  # <-- Add this import

urlpatterns = [
    path('admin/', admin.site.urls),
    # Any request to the root URL will be handled by our landing app's urls
    path('', include('landing.urls')),
    # Add the parser app's urls
    path('parser/', include('parser.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # --- Add this line to serve the team_pics folder ---
    urlpatterns += static('/team_pics/', document_root=os.path.join(settings.BASE_DIR, 'team_pics'))