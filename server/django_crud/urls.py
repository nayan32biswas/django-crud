from django.contrib import admin
from django.conf import settings
from django.urls import path, include

from .views import home_view
from accounts.urls import urlpatterns as accounts_urls
from checkout.urls import urlpatterns as checkout_urls
from order.urls import urlpatterns as order_urls
from product.urls import urlpatterns as product_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("accounts/", include((accounts_urls, "accounts"), namespace="accounts")),
    path("checkout/", include((checkout_urls, "checkout"), namespace="checkout")),
    path("order/", include((order_urls, "order"), namespace="order")),
    path("product/", include((product_urls, "product"), namespace="product")),
    path("", home_view),
]


if settings.DEBUG is True:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
