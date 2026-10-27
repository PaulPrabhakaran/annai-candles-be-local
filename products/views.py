from __future__ import annotations

import logging
import math
import secrets
from datetime import timedelta


from django.http import Http404
from django.db.models import Q

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db import IntegrityError, transaction
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import APIException, ValidationError, NotFound

from annai_candles_be.pagination import paginate_queryset, empty_paginated_data
from annai_candles_be.common import custom_error_message, permission_denied_message
from annai_candles_be.response import api_error_response, api_response, frontend_error_response
from annai_candles_be.helpers import ensure_admin

from products.models import Product, ProductPriceForCustomer
from products.serializers import (ProductSerializer, ProductListSerializer,
                        AssignCustomerPricesSerializer, CustomerPriceItemSerializer,
                        ProductUnitPriceDetailSerializer, ProductPriceForCustomerResponseSerializer)


logger = logging.getLogger('annai_candles_be')


class AddProductAPIView(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            denied = ensure_admin(request)
            if denied:
                return denied            
            
            serializer = ProductSerializer(
                data=request.data,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            res = serializer.save()
            return api_response(
                'Product Added Successfully',
                data = ProductListSerializer(
                    res,
                    context={"request": request},
                ).data,
                http_status=status.HTTP_201_CREATED
            )
            
        except APIException as api_exception:
            logger.exception("Add Product Error - %s", api_exception)            
            return frontend_error_response(api_exception)
        except Exception as e:
            logger.exception("Add Product Error - %s", e)
            raise APIException({"message": custom_error_message})
        
        
        
        
        
        



class UpdateProductAPIView(APIView):
    @transaction.atomic
    def put(self, request, product_id):
        try:
            denied = ensure_admin(request)
            if denied:
                return denied
            
            obj = get_object_or_404(Product, pk=product_id)         
            
            serializer = ProductSerializer(
                obj,
                data=request.data,
                partial=True,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            res = serializer.save()
            return api_response(
                'Product Added Successfully',
                data = ProductListSerializer(
                    res,
                    context={"request": request},
                ).data,
                http_status=status.HTTP_201_CREATED
            )
            
        except APIException as api_exception:
            logger.exception("Update Product Error - %s", api_exception)            
            return frontend_error_response(api_exception)
        except Exception as e:
            logger.exception("Update Product Error - %s", e)
            raise APIException({"message": custom_error_message})
        
        
        
        
    
    
class GetAllProductsAPIView(APIView):
    def get(self, request):
        try:
            queryset = Product.objects.select_related('category').all()
            
            status_param = (request.query_params.get("status") or "").strip().lower()
            if status_param in ("true", "1"):
                queryset = queryset.filter(status=True)
            elif status_param in ("false", "0"):
                queryset = queryset.filter(status=False)
                
                
            
            search = (request.query_params.get("search") or "").strip()
            if search:
                queryset = queryset.filter(
                    Q(id__contains=search)
                    | Q(name__icontains=search)
                    | Q(category__name__icontains=search)
                    | Q(serial_number__icontains=search)
                    | Q(hsn_code__icontains=search)
                )
                
            
            page_items, pagination = paginate_queryset(queryset, request)
            return api_response(
                "Products fetched successfully",
                data={
                    "results": ProductListSerializer(page_items, many=True).data,
                    "pagination": pagination,
                },
            )
            
            
                
        except Exception as e:
            logger.exception("Product Get-All List Error - %s", e)
            return api_response(
                custom_error_message,
                data=empty_paginated_data(request),
            )
            
            
            



class GetIndividualProductAPIView(APIView):
    def get(self, request, product_id):
        try:
            obj = get_object_or_404(Product, pk=product_id)
            data = ProductSerializer(obj).data
        except Exception as e:
            logger.exception(f"Get Individual Product Error - {e}")
            data = None
            
        return Response({'data' : data})
    
    
    


class AssignProductPriceForCustomerAPIView(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            denied = ensure_admin(request)
            if denied:
                return denied
            
            
            serializer = AssignCustomerPricesSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            customer = serializer.validated_data["customer"]
            prices = serializer.validated_data["prices"]

            unit_price_ids = [
                item["unit_price"].id for item in prices
            ]

            existing_prices = ProductPriceForCustomer.objects.filter(
                customer=customer,
                unit_price_id__in=unit_price_ids,
            )

            existing_map = {
                obj.unit_price_id: obj
                for obj in existing_prices
            }

            to_create = []
            to_update = []

            for item in prices:
                unit_price = item["unit_price"]
                price = item["price"]

                existing_obj = existing_map.get(unit_price.id)

                if existing_obj:
                    existing_obj.price = price
                    existing_obj.updated_by = request.user
                    to_update.append(existing_obj)
                else:
                    to_create.append(
                        ProductPriceForCustomer(
                            customer=customer,
                            unit_price=unit_price,
                            price=price,
                            created_by=request.user,
                            updated_by=request.user,
                        )
                    )

            if to_create:
                ProductPriceForCustomer.objects.bulk_create(to_create)

            if to_update:
                ProductPriceForCustomer.objects.bulk_update(
                    to_update,
                    ["price", "updated_by", "updated_at"],
                )

            result = ProductPriceForCustomer.objects.filter(
                customer=customer,
                unit_price_id__in=unit_price_ids,
            ).select_related(
                "customer",
                "unit_price",
                "unit_price__unit",
                "unit_price__product",
                "unit_price__product__category",
            ).order_by("id")

            
            return api_response(
                'Product Assigned Successfully',
                data = ProductPriceForCustomerResponseSerializer(
                    result,
                    many=True,
                ).data,
                http_status=status.HTTP_201_CREATED
            )
            
            
        except APIException as api_exception:
            logger.exception("Assign Product Price For Customer Exception - %s", api_exception)            
            return frontend_error_response(api_exception)
        except Exception as e:
            logger.exception("Assign Product Price For Customer Error - %s", e)
            raise APIException({"message": custom_error_message})
        
        
        
        


class GetAssignedCustomerPriceAPIView(APIView):
    def get(self, request):
        try:
            queryset = ProductPriceForCustomer.objects.select_related(
                "customer",
                "unit_price",
                "unit_price__unit",
                "unit_price__product",
                "unit_price__product__category",
            ).order_by("id")
            
            search = (request.query_params.get("search") or "").strip()
            if search:
                queryset = queryset.filter(
                    Q(id__contains=search)
                    | Q(customer__name__icontains=search)
                )
                
                
            page_items, pagination = paginate_queryset(queryset, request)
            return api_response(
                "Data fetched successfully",
                data={
                    "results": ProductPriceForCustomerResponseSerializer(page_items, many=True).data,
                    "pagination": pagination,
                },
            )                      
            
        except Exception as e:
            logger.exception("Get Assigned Customer Price Error - %s", e)
            return api_response(
                custom_error_message,
                data=empty_paginated_data(request),
            )