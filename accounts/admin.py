"""Admin configuration for accounts app."""

from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""

    list_display = (
        "email",
        "first_name",
        "last_name",
        "phone",
        "is_active",
        "is_staff",
        "created_at",
        "deleted_at",
    )
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "created_at",
        "updated_at",
        "deleted_at",
    )
    search_fields = ("email", "first_name", "last_name", "phone")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "phone")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                    "created_at",
                    "updated_at",
                    "deleted_at",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "phone",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    readonly_fields = ("created_at", "updated_at", "last_login", "date_joined")

    def get_queryset(self, request: HttpRequest) -> QuerySet[User]:
        """Filter out soft-deleted users by default."""
        qs = super().get_queryset(request)
        return qs.filter(deleted_at__isnull=True)

    def soft_delete_users(self, request: HttpRequest, queryset: QuerySet[User]) -> None:
        """Admin action to soft delete users."""
        count = 0
        for user in queryset:
            user.soft_delete()
            count += 1
        self.message_user(request, f"{count} user(s) were successfully soft deleted.")

    soft_delete_users.short_description = "Soft delete selected users"

    def restore_users(self, request: HttpRequest, queryset: QuerySet[User]) -> None:
        """Admin action to restore soft-deleted users."""
        count = 0
        for user in queryset:
            user.restore()
            count += 1
        self.message_user(request, f"{count} user(s) were successfully restored.")

    restore_users.short_description = "Restore selected users"

    actions = [soft_delete_users, restore_users]

    def get_actions(self, request: HttpRequest) -> dict[str, Any]:
        """Get available actions based on queryset."""
        actions = super().get_actions(request)
        if (
            "deleted_at__isnull" in request.GET
            and request.GET["deleted_at__isnull"] == "False"
        ):
            # If viewing deleted users, show restore action
            if "soft_delete_users" in actions:
                del actions["soft_delete_users"]
        else:
            # If viewing active users, show soft delete action
            if "restore_users" in actions:
                del actions["restore_users"]
        return actions
