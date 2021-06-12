from django.contrib import admin
from django.conf import settings
from django.urls import path, include

from accounts.urls import urlpatterns as accounts_urls
from .views import home_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path('accounts/', include((accounts_urls, "accounts"), namespace='accounts')),
    path("", home_view),
]


if settings.DEBUG is True:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
