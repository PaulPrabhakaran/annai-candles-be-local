"""Pagination helpers for auction list APIs."""

from __future__ import annotations

from django.core.paginator import EmptyPage, Paginator
from rest_framework.exceptions import ValidationError


def paginate_queryset(queryset, request, default_page_size=10, max_page_size=100):
    """
    Paginate a queryset from request query params.

    Query params:
      - page (default 1)
      - page_size (default 10, max 100)

    Returns (page_items, pagination_meta).
    """
    try:
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", default_page_size))
    except (TypeError, ValueError):
        raise ValidationError({"message": "page and page_size must be integers."})

    if page < 1:
        raise ValidationError({"message": "page must be >= 1."})
    if page_size < 1:
        raise ValidationError({"message": "page_size must be >= 1."})
    if page_size > max_page_size:
        page_size = max_page_size

    paginator = Paginator(queryset, page_size)
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages if paginator.num_pages else 1)

    pagination = {
        "count": paginator.count,
        "page": page_obj.number,
        "page_size": page_size,
        "total_pages": paginator.num_pages,
        "next": page_obj.next_page_number() if page_obj.has_next() else None,
        "previous": page_obj.previous_page_number() if page_obj.has_previous() else None,
    }
    return page_obj.object_list, pagination





def empty_paginated_data(request):
    try:
        page = int(request.query_params.get("page", 1))
    except (TypeError, ValueError):
        page = 1
    try:
        page_size = int(request.query_params.get("page_size", 10))
    except (TypeError, ValueError):
        page_size = 10
    return {
        "results": [],
        "pagination": {
            "count": 0,
            "page": page if page >= 1 else 1,
            "page_size": page_size if page_size >= 1 else 10,
            "total_pages": 0,
            "next": None,
            "previous": None,
        },
    }
