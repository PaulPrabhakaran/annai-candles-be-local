from django.urls import path
from products import views


urlpatterns = [
    path('add/', views.AddProductAPIView.as_view(), name="add-product"),
    path('update/<int:product_id>/', views.UpdateProductAPIView.as_view(), name="update-product"),
    path('get-all/', views.GetAllProductsAPIView.as_view(), name="get-all-products"),
    path('<int:product_id>/', views.GetIndividualProductAPIView.as_view(), name="get-individual-product"),
    path('assign-price-for-customer/', views.AssignProductPriceForCustomerAPIView.as_view(), name='assign-price-for-customer'),
    path('get-assigned-price-for-customer/', views.GetAssignedCustomerPriceAPIView.as_view(), name="get-assigned-price-for-customer"),
]