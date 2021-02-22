from django.contrib import admin
from django.urls import path, include
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('core.urls', namespace='core')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__DEBUG__/', include(debug_toolbar.urls))]


