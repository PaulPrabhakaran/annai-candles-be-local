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
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from annai_candles_be.common import custom_error_message, permission_denied_message
from annai_candles_be.pagination import paginate_queryset, empty_paginated_data
from annai_candles_be.response import api_error_response, api_response, frontend_error_response
from annai_candles_be.helpers import ensure_admin
from users.choices import LoginActivityTypeChoices, UserRoleChoices
from users.models import User, UserProfile
from users.serializers import (LoginSerializer, LogoutSerializer, UserDetailSerializer,
                               AddNewMemberSerializer, UpdateProfileSerializer, 
                               UpdateMemberSerializer)
from users.actions import record_login_logout_activity




logger = logging.getLogger('annai_candles_be')

class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    
    @transaction.atomic
    def post(self, request):
        try:
            logger.debug("User Login Username - %s", request.data.get("username"))
            serializer = LoginSerializer(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data["user"]
            
            refresh = RefreshToken.for_user(user)
            record_login_logout_activity(
                request, user, LoginActivityTypeChoices.LOGIN
            )
            return api_response(
                "Login successful",
                data={
                    "token": {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                    },
                    "user": UserDetailSerializer(user).data
                },
            )
        except APIException as api_exception:
            logger.exception("User Login Error - %s", api_exception)
            return frontend_error_response(api_exception)
        except Exception as e:
            logger.exception("User Login Error - %s", e)
            raise APIException({"message": custom_error_message}) 
        
        
        



class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        try:
            logger.info("User Logout - %s", request.user.email)
            serializer = LogoutSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            refresh = RefreshToken(serializer.validated_data["refresh"])
            refresh.blacklist()
            record_login_logout_activity(
                request, request.user, LoginActivityTypeChoices.LOGOUT
            )

            return api_response("Logged out successfully")
        except TokenError:
            logger.exception("User Logout Error - invalid refresh token")
            return frontend_error_response("Invalid or expired refresh token")
        except APIException as api_exception:
            logger.exception("User Logout Error - %s", api_exception)            
            return frontend_error_response(api_exception)
        except Exception as e:
            logger.exception("User Logout Error - %s", e)
            raise APIException({"message": custom_error_message})
        
        
        
        




class AddNewMemberAPIView(APIView):  
    @transaction.atomic  
    def post(self, request):
        try:
            denied = ensure_admin(request)
            if denied:
                return denied            
            
            serializer = AddNewMemberSerializer(
                data=request.data, context={"request": request}
            )
            
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            
            return api_response(
                "Member Created successfully",
                data = UserDetailSerializer(user).data,
                http_status=status.HTTP_201_CREATED,
            )
            
        except ValidationError:
            raise
        except APIException as api_exception:
            logger.exception("Add New Sales Man Error - %s", api_exception)
            return frontend_error_response(api_exception)
        except Exception as e:
            logger.exception("Add New Sales Man Error - %s", e)
            raise APIException({"message": custom_error_message})
        
        
        
        


class ProfileAPIView(APIView):
    
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    @transaction.atomic
    def put(self, request):
        try:
            logger.debug("REq Data - %s", request.data)
            serializer = UpdateProfileSerializer(
                instance=request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return api_response(
                "Profile Updated successfully",
                data = UserDetailSerializer(user).data,
                http_status=status.HTTP_200_OK,
            )
        except APIException as api_exception:
            logger.exception("Profile Update Api Exception - %s", api_exception)
            return frontend_error_response(api_exception)
        except Exception as e:
            logger.exception("Profile Update Error - %s", e)
            raise APIException({"message": custom_error_message})

        

        




class GetAllMembers(APIView):
    def get(self, request):
        try:
            denied = ensure_admin(request)
            if denied is not None:
                return denied
            
            queryset = User.objects.select_related('user_profile').all()
            
            status_param = (request.query_params.get("status") or "").strip().lower()
            if status_param in ("true", "1"):
                queryset = queryset.filter(status=True)
            elif status_param in ("false", "0"):
                queryset = queryset.filter(status=False)
                
            role_param = (request.query_params.get("role") or "").strip().lower()
            if role_param in ("salesman", UserRoleChoices.SALESMAN):
                queryset = queryset.filter(role=UserRoleChoices.SALESMAN)
            elif role_param in ("admin", UserRoleChoices.ADMIN):
                queryset = queryset.filter(role=UserRoleChoices.SALESMAN)
                
            
            search = (request.query_params.get("search") or "").strip()
            if search:
                queryset = queryset.filter(
                    Q(id__contains=search)
                    | Q(first_name__icontains=search)
                    | Q(last_name__icontains=search)
                    | Q(phone__icontains=search)
                    | Q(email__icontains=search)
                )
                
            
            page_items, pagination = paginate_queryset(queryset, request)
            return api_response(
                "Customers fetched successfully",
                data={
                    "results": UserDetailSerializer(page_items, many=True).data,
                    "pagination": pagination,
                },
            )
        
        except Exception as e:
            logger.exception("Member Get-All List Error - %s", e)
            return api_response(
                custom_error_message,
                data=empty_paginated_data(request),
            )
        
        
        
        


class GetIndividualMember(APIView):
    def get(self, request, user_id):
        data = None
        try:
            obj = get_object_or_404(User, pk=user_id)
            data = UserDetailSerializer(obj).data
        except Exception as e:
            logger.exception(f"Get Individual Member Data - {e}")
            data = None
        
        return Response({'data' : data})
    
    




class UpdateMember(APIView):
    @transaction.atomic
    def put(self, request, member_id):
        try:
            denied = ensure_admin(request)
            if denied:
                return denied
            
            
            obj = get_object_or_404(User, pk=member_id)                        
            
            serializer = UpdateMemberSerializer(
                obj, data=request.data, partial=True
            )
            
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            
            return api_response(
                "Member Updated successfully",
                data = UserDetailSerializer(user).data,
                http_status=status.HTTP_200_OK,
            )
        
        except (Http404, NotFound):
            return api_error_response('Member not found', http_status=400)
        
        
        except APIException as api_exception:
            logger.exception("Update Member Api Exception - %s", api_exception)
            return frontend_error_response(api_exception)
        except Exception as e:
            logger.exception("Update Member Error - %s", e)
            raise APIException({"message": custom_error_message})








class ActivateOrDeactivateMember(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            denied = ensure_admin(request)
            if denied is not None:
                return denied
            
            
            member_id = request.data.get('member_id', None)
            status_code = request.data.get('status', None)
            
            if member_id is None or status_code is None:
                return api_error_response(
                    'Member Id or Status is Missing'
                )                
            
            active_values = (1, "1", True, "true")
            status = status_code in active_values
            status_text = "Activated" if status else "Deactivated"
            
            obj = get_object_or_404(User, pk=member_id)
            obj.is_active = status
            obj.updated_by = request.user
            obj.save()
            
            return Response({'message' : f'Member {status_text} Successfully'})
            
        except (Http404, NotFound):
            return api_error_response('Member not found', http_status=400) 
            
        except APIException as api_exception:
            logger.exception("Activate Or Deactivate Member Api Exception - %s", api_exception)
            return frontend_error_response(api_exception)
        except Exception as e:
            logger.exception("Activate Or Deactivate Member Error - %s", e)
            raise APIException({"message": custom_error_message})