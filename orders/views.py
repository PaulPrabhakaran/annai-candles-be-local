from __future__ import annotations

import logging
import math
import secrets
from datetime import timedelta
from django.utils.timezone import now


from django.http import Http404

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.exceptions import APIException, ValidationError, NotFound
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response

from annai_candles_be.common import custom_error_message, permission_denied_message
from annai_candles_be.response import api_error_response, api_response, frontend_error_response
from annai_candles_be.helpers import ensure_admin

from products.models import Product, ProductUnitPrice, ProductPriceForCustomer


from orders.models import Orders, OrderItems
from orders.serializers import CreateOrderSerializer

from orders.choices import DiscountType


logger = logging.getLogger('annai_candles_be')



class GetProductSellingPriceForCustomerAPIView(APIView):
    def get(self, request):
        price = 0
        try:
            customer = request.query_params.get('customer', None)
            product = request.query_params.get('product', None)
            unit = request.query_params.get('unit', None)
            
            if customer == None or product == None or unit == None:
                price = 0
            else:
                product_price_for_customer = ProductPriceForCustomer.objects.filter(
                    customer = customer,
                    unit_price__product = product,
                    unit_price__unit = unit
                ).first()
                
                if product_price_for_customer:
                    price = product_price_for_customer.price or 0
                else:
                    product_unit_price = ProductUnitPrice.objects.filter(
                        product = product,
                        unit = unit,
                        status = True
                    ).first()
                    
                    if product_unit_price:
                        price = product_unit_price.price or 0
                    
            
        except Exception as e:
            logger.exception(f"Get Product Price For customer Error - {e}")
            price = 0
            
        return Response({'data' : price})
    
    
    
    
    
class CreateOrderAPIView(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            data = request.data
            
            order_serializer = CreateOrderSerializer(data=data)
            order_serializer.is_valid(raise_exception=True)
            
            customer = order_serializer.validated_data['customer']            
            items = order_serializer.validated_data['items']            
            common_discount_type = order_serializer.validated_data['common_discount_type']            
            common_discount_value = order_serializer.validated_data['common_discount_value']            
            common_discount_amount = order_serializer.validated_data['common_discount_amount']            
            
            order = order_serializer.save(
                order_taken_by=request.user,
                created_by=request.user,
                created_at=now()
            )            
            
            order_sub_total = 0
            order_item_discount_total = 0
            order_total_qty = 0
            
            
            for item in items:
                product = item['product']
                unit = item['unit']
                qty = item['qty']
                discount_type = item['discount_type']
                discount_value = item['discount_value']
                discount_amount = item['discount_amount']
                
                this_price = 0
                
                product_price_for_customer = ProductPriceForCustomer.objects.filter(
                    customer = customer,
                    unit_price__product = product,
                    unit_price__unit = unit
                ).first()
                
                if product_price_for_customer:
                    this_price = product_price_for_customer.price or 0
                else:
                    product_unit_price = ProductUnitPrice.objects.filter(
                        product = product,
                        unit = unit,
                        status = True
                    ).first()
                    
                    if product_unit_price:
                        this_price = product_unit_price.price or 0
                        
                        
                
                sub_total = round((float(this_price) * float(qty)),2)
                              
                
                if discount_type == DiscountType.NONE:
                    total_amount = sub_total
                    discount_value = 0
                    discount_amount = 0
                else:                    
                    if discount_type == DiscountType.PERCENTAGE:
                        amount_to_reduce = float(sub_total) * float(round((discount_value / 100)),2)
                        discount_amount = amount_to_reduce                        
                        total_amount = round((float(sub_total) - float(discount_amount)),2)
                    else:
                        discount_amount = discount_value
                        total_amount = round((float(sub_total) - float(discount_amount)),2)
                        
                    
                    order_item_discount_total = float(order_item_discount_total) + float(discount_amount)
                        
                
                if float(total_amount) <= 0:
                    return api_error_response(f'Amount is 0 for Product {product.name} Unit {unit.name}')
                        
                        
                
                order_sub_total = float(order_sub_total) + float(total_amount)
                order_total_qty = float(order_total_qty) + float(qty)
                
                
                OrderItems.objects.create(
                    order = order,
                    product = product,
                    unit = unit,
                    product_name = product.name,
                    unit_name = unit.name,
                    qty = qty,
                    unit_price_amount = this_price,
                    sub_total = this_price,
                    discount_type = discount_type,
                    discount_value = discount_value,
                    discount_amount = discount_amount,
                    total_amount = total_amount,
                    created_at = now()
                )
                
                
            order_total_amount = 0
            
            if common_discount_type == DiscountType.NONE:
                order_total_amount = order_sub_total
                common_discount_value = 0
                common_discount_amount = 0
            else:                    
                if common_discount_type == DiscountType.PERCENTAGE:
                    amount_to_reduce = float(order_sub_total) * float(round((common_discount_value / 100)),2)
                    common_discount_amount = amount_to_reduce                        
                    order_total_amount = round((float(order_sub_total) - float(common_discount_amount)),2)
                else:
                    common_discount_amount = common_discount_value
                    order_total_amount = round((float(order_sub_total) - float(common_discount_amount)),2)
                    
                    
            
            if float(order_total_amount) <= 0:
                return api_error_response(f'Total amount Cannot be 0 or less')
            
            
            order.total_items = len(items)
            order.total_qty = order_total_qty
            order.sub_total = order_sub_total
            order.item_discount_total = order_item_discount_total
            order.common_discount_type = common_discount_type
            order.common_discount_value = common_discount_value
            order.common_discount_amount = common_discount_amount
            order.total_amount = order_total_amount
            order.save()               
            
            
            
            
            return api_response(
                'Order Created Successfully',
                data = [],
                http_status=status.HTTP_201_CREATED
            ) 
        except APIException as api_exception:
            logger.exception("Assign Product Price For Customer Exception - %s", api_exception)            
            return frontend_error_response(api_exception)
        except Exception as e:
            logger.exception("Assign Product Price For Customer Error - %s", e)
            raise APIException({"message": custom_error_message})
        