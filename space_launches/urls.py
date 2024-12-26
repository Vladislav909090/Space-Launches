from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from .views import home

urlpatterns = [
    path('', home, name='home'),
    path("admin/", admin.site.urls),
    path('users/', include('users.urls')),
    path('space_data/', include('space_data.urls')),
]




if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)