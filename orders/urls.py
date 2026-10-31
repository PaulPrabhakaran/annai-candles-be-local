from django.urls import path

from orders import views


urlpatterns = [
    path('get-product-selling-price-for-customer/', views.GetProductSellingPriceForCustomerAPIView.as_view(), name="get-product-selling-price-for-customer"),
]