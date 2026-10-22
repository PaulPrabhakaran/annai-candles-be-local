from django.urls import path
from unit import views


urlpatterns = [
    path("", views.UnitApiView.as_view(), name="unit-api-view"),
    path("<int:unit_id>/", views.UnitDetailApiView.as_view(), name="unit-detail-api-view"),
    path("activate-or-deactivate/", views.ActivateOrDeactivateUnit.as_view(), name="activate-or-deactivate-unit")
]
