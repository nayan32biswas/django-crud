from django.urls import path

from django.contrib.auth.decorators import login_required
from . import views


urlpatterns = [
    path("", login_required(views.OrderListView.as_view()), name="order-list"),
    path(
        "<int:pk>/",
        login_required(views.OrderDetailView.as_view()),
        name="order-detail",
    ),
    path(
        "invoice/<int:pk>/",
        login_required(views.GeneratePDF.as_view()),
        name="download-invoice",
    ),
]
