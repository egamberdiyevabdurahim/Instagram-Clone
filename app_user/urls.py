from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from app_user import views


urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('register/', views.RegisterView.as_view()),
    # path('logout/', views.LogoutView.as_view()),

    path('profile/<int:pk>/', views.ProfileView.as_view()),

    path('<int:user_id>/follow/', views.FollowListView.as_view()),
    path('followers/<int:user_id>/', views.FollowersListView.as_view()),
    path('following/<int:user_id>/', views.FollowingListView.as_view()),

    path('resend-email/', views.ResendEmailConfirmation.as_view()),
    path('verify-email/', views.VerifyEmailConfirmation.as_view()),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]