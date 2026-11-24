
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from farm import views as farm_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Language Selection
    path('i18n/', include('django.conf.urls.i18n')),

    # Application URLs
    path('accounts/', include('accounts.urls')),
    path('farm/', include('farm.urls')),
    path('finance/', include('finance.urls')),
    path('inventory/', include('inventory.urls')),
    path('ai/', include('ai_assistant.urls')),

    # Home Dashboard
    path('', farm_views.dashboard, name='home'),
]

# Media Files - Development Only
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
