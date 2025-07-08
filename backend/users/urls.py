from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('preferences/', views.JobPreferenceListCreateView.as_view(), name='job_preferences'),
    path('preferences/<int:pk>/', views.JobPreferenceDetailView.as_view(), name='job_preference_detail'),
]