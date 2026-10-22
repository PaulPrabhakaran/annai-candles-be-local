from __future__ import annotations

import logging
import math
import secrets
from datetime import timedelta
from django.db.models import Q

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
from annai_candles_be.pagination import paginate_queryset, empty_paginated_data
from annai_candles_be.response import api_error_response, api_response, frontend_error_response
from annai_candles_be.helpers import ensure_admin

from customer.models import Customer
from customer.serializers import CustomerSerializer

logger = logging.getLogger('annai_candles_be')





class CustomerApiView(APIView):    
    @transaction.atomic
    def post(self, request):
        try:
            denied = ensure_admin(request)
            if denied:
                return denied
            serializer = CustomerSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            res = serializer.save(created_by=request.user)
            return api_response(
                "Customer Added Successfully",
                data = CustomerSerializer(res).data,
                http_status=status.HTTP_201_CREATED
            )
        except APIException as api_exception:
            logger.exception("Add Customer Error - %s", api_exception)            
            return frontend_error_response(api_exception)
        except Exception as e:
            logger.exception("Add Customer Error - %s", e)
            raise APIException({"message": custom_error_message})
            
    


class CustomerDetailApiView(APIView):
    def get(self, request, customer_id):
        data = None
        try:
            obj = get_object_or_404(Customer, pk=customer_id)
            data = CustomerSerializer(obj).data
        except Exception as e:
            logger.exception(f"Get customer Detail Api Error - {e}")
            data = None
        
        return Response({'data' : data})
    
    
    @transaction.atomic
    def put(self, request, customer_id):
        try:
            denied = ensure_admin(request)
            if denied:
                return denied
            obj = get_object_or_404(Customer, pk=customer_id)
            serializer = CustomerSerializer(obj, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            res = serializer.save(updated_by=request.user)
            
            return api_response(
                'Customer Updated successfully',
                data = CustomerSerializer(res).data
            )
        
        except (Http404, NotFound):
            return api_error_response('Customer not found', http_status=400)
            
        except APIException as api_exception:
            logger.exception("Update Customer Error - %s", api_exception)            
            return frontend_error_response(api_exception)
        except Exception as e:
            logger.exception("Update Customer Error - %s", e)
            raise APIException({"message": custom_error_message})
        
        
        



class GetAllCustomers(APIView):
    def get(self, request):
        try:            
            queryset = Customer.objects.all()
            
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
                    | Q(store_name__icontains=search)
                    | Q(address__icontains=search)
                )
                
            
            page_items, pagination = paginate_queryset(queryset, request)
            return api_response(
                "Customers fetched successfully",
                data={
                    "results": CustomerSerializer(page_items, many=True).data,
                    "pagination": pagination,
                },
            )
        
        except Exception as e:
            logger.exception("Member Get-All List Error - %s", e)
            return api_response(
                custom_error_message,
                data=empty_paginated_data(request),
            )
            
            
            
            
            

class ActivateOrDeactivateCustomer(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            denied = ensure_admin(request)
            if denied is not None:
                return denied
            
            print(f"Data - {request.data}")
            
            customer_id = request.data.get('customer_id', None)
            status_code = request.data.get('status', None)
            
            if customer_id is None or status_code is None:
                return api_error_response(
                    'Customer Id or Status is Missing'
                )                
            
            active_values = (1, "1", True, "true")
            status = status_code in active_values
            status_text = "Activated" if status else "Deactivated"
            
            obj = get_object_or_404(Customer, pk=customer_id)
            obj.status = status
            obj.updated_by = request.user
            obj.save()
            
            return Response({'message' : f'Customer {status_text} Successfully'})           
        
        except (Http404, NotFound):
            return api_error_response('Customer not found', http_status=400)
            
        except APIException as api_exception:
            logger.exception("Activate Or Deactivate Customer Api Exception - %s", api_exception)
            return frontend_error_response(api_exception)
        except Exception as e:
            logger.exception("Activate Or Deactivate Customer Error - %s", e)
            raise APIException({"message": custom_error_message})