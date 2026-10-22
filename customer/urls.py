from django.urls import path
from customer import views


urlpatterns = [
    path("", views.CustomerApiView.as_view(), name="customer-api-view"),
    path("<int:customer_id>/", views.CustomerDetailApiView.as_view(), name="customer-detail-api-view"),
    path("get-all/", views.GetAllCustomers.as_view(), name="get-all-customer"),
    path("activate-or-deactivate/", views.ActivateOrDeactivateCustomer.as_view(), name="activate-or-deactivate-customer")
]
