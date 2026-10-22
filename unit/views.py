from __future__ import annotations

import logging
import math
import secrets
from datetime import timedelta


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

from unit.models import Unit
from unit.serializers import UnitSerializer

logger = logging.getLogger('annai_candles_be')





class UnitApiView(APIView):
    def get(self, request):
        try:
            data = UnitSerializer(Unit.objects.all(), many=True).data
        except Exception as e:
            logger.exception(f"Get Unit Data Error - {e}")
            data = []
            
        return Response({'data' : data})
    
    
    @transaction.atomic
    def post(self, request):
        try:
            denied = ensure_admin(request)
            if denied:
                return denied
            serializer = UnitSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            res = serializer.save(created_by=request.user)
            return api_response(
                "Unit Added Successfully",
                data = UnitSerializer(res).data,
                http_status=status.HTTP_201_CREATED
            )
        except APIException as api_exception:
            logger.exception("Add Unit Error - %s", api_exception)            
            return frontend_error_response(api_exception)
        except Exception as e:
            logger.exception("Add Unit Error - %s", e)
            raise APIException({"message": custom_error_message})
            
    


class UnitDetailApiView(APIView):
    def get(self, request, unit_id):
        data = None
        try:
            obj = get_object_or_404(Unit, pk=unit_id)
            data = UnitSerializer(obj).data
        except Exception as e:
            logger.exception(f"Get unit Detail Api Error - {e}")
            data = None
        
        return Response({'data' : data})
    
    
    @transaction.atomic
    def put(self, request, unit_id):
        try:
            denied = ensure_admin(request)
            if denied:
                return denied
            obj = get_object_or_404(Unit, pk=unit_id)
            serializer = UnitSerializer(obj, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            res = serializer.save(updated_by=request.user)
            
            return api_response(
                'Unit Updated successfully',
                data = UnitSerializer(res).data
            )
            
        
        except (Http404, NotFound):
            return api_error_response('Unit not found', http_status=400)
        
        
            
        except APIException as api_exception:
            logger.exception("Update Unit Error - %s", api_exception)            
            return frontend_error_response(api_exception)
        except Exception as e:
            logger.exception("Update Unit Error - %s", e)
            raise APIException({"message": custom_error_message})
        
        
        
        
        




class ActivateOrDeactivateUnit(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            denied = ensure_admin(request)
            if denied is not None:
                return denied
                        
            unit_id = request.data.get('unit_id', None)
            status_code = request.data.get('status', None)
            
            if unit_id is None or status_code is None:
                return api_error_response(
                    'Unit Id or Status is Missing'
                )                
            
            active_values = (1, "1", True, "true")
            status = status_code in active_values
            status_text = "Activated" if status else "Deactivated"
                        
            obj = get_object_or_404(Unit, pk=unit_id)
            obj.status = status
            obj.updated_by = request.user
            obj.save()
            
            return Response({'message' : f'Unit {status_text} Successfully'})           
            
        
        except (Http404, NotFound):
            return api_error_response('Unit not found', http_status=400)
        
        except APIException as api_exception:
            logger.exception("Activate Or Deactivate Unit Api Exception - %s", api_exception)
            return frontend_error_response(api_exception)
        except Exception as e:
            logger.exception("Activate Or Deactivate Unit Error - %s", e)
            raise APIException({"message": custom_error_message})
            