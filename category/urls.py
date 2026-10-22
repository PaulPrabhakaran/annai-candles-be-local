from django.urls import path
from category import views


urlpatterns = [
    path("", views.CategoryApiView.as_view(), name="category-api-view"),
    path("<int:category_id>/", views.CategoryDetailApiView.as_view(), name="category-detail-api-view"),
    path("activate-or-deactivate/", views.ActivateOrDeactivateCategory.as_view(), name="activate-or-deactivate-category")
]
