"""URLs for accounts app."""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

app_name = 'accounts'

urlpatterns = [
    # Web pages
    path('login/', views.login_page_view, name='login_page'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # API Authentication endpoints
    path('api/register/', views.UserRegistrationView.as_view(), name='register'),
    path('api/login/', views.UserLoginView.as_view(), name='login'),
    path('api/logout/', views.logout_view, name='logout'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API User profile endpoints
    path('api/profile/', views.UserProfileView.as_view(), name='profile'),
    path(
        'api/change-password/',
        views.ChangePasswordView.as_view(),
        name='change_password'
    ),
    path('api/me/', views.user_info_view, name='user_info'),
]