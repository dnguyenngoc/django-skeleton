"""URLs for accounts app."""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

app_name = "accounts"

urlpatterns = [
    # Web pages
    path("login/", views.login_page_view, name="login_page"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("profile/", views.profile_view, name="profile"),
    path("settings/", views.settings_view, name="settings"),
    # API Authentication endpoints
    path("api/auth/register/", views.UserRegistrationView.as_view(), name="register"),
    path("api/auth/login/", views.UserLoginView.as_view(), name="login"),
    path("api/auth/logout/", views.logout_view, name="logout"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # API User profile endpoints
    path("api/auth/profile/", views.UserProfileView.as_view(), name="profile"),
    path(
        "api/auth/change-password/",
        views.ChangePasswordView.as_view(),
        name="change_password",
    ),
    path("api/auth/me/", views.user_info_view, name="user_info"),
    path("api/auth/check/", views.check_auth_view, name="check_auth"),
    path("api/auth/create-session/", views.create_session_view, name="create_session"),
    path("api/auth/refresh/", views.refresh_token_view, name="refresh_token"),
]
