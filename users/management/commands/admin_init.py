from __future__ import annotations

import os
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from users.choices import UserRoleChoices
from users.models import User, UserProfile


class Command(BaseCommand):   

    help = "Seed the initial admin user and AdminProfile when missing."

    def handle(self, *args: Any, **options: Any) -> None:
        with transaction.atomic():
            phone = os.getenv("ADMIN_PHONE") or ""
            password = os.getenv("ADMIN_PASSWORD") or ""
            first_name = (os.getenv("ADMIN_FIRSTNAME") or "").strip()

            if not phone:
                raise CommandError("ADMIN_PHONE is not set in the environment.")
            if not password:
                raise CommandError("ADMIN_PASSWORD is not set in the environment.")

            existing = User.objects.filter(phone__iexact=phone).first()
            if existing is not None:
                UserProfile.objects.get_or_create(user=existing)
                self.stdout.write(
                    self.style.WARNING(
                        f"Admin user already exists for Phone '{phone}'. Skipping create."
                    )
                )
                return

            
            user = User.objects.create_user(
                phone=phone,
                username=phone,
                password=password,
                role=UserRoleChoices.ADMIN,
                is_staff=False,
                is_superuser=False,
                first_name=first_name or "Admin",
            )
            UserProfile.objects.get_or_create(user=user)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Created admin user '{user.phone}' with AdminProfile."
                )
            )
