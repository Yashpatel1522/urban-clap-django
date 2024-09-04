from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    RegisterView,
    LoginView,
    ProfileView,
    UserViewSet,
    ChangePasswordViewSet,
    ForgetPasswordViewSet,
    LogoutView,
    ProfileList,
    PasswordResetConfrimView,
    UserView,
    CustomUserCreate,
    UpdateProfile,
    UserData,
)
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import routers


router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"userdata", UserData, basename="userdata")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth_register"),
    path("login/", LoginView.as_view(), name="token_obtain_pair"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("change-password/", ChangePasswordViewSet.as_view(), name="change_password"),
    path("forgot-password/", ForgetPasswordViewSet.as_view(), name="forgot_password"),
    path(
        "password_reset_confrim/",
        PasswordResetConfrimView.as_view(),
        name="password_reset_confrim",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("getuser/", UserView.as_view(), name="user"),
    path("profilephoto/", ProfileList.as_view(), name="profile_photo"),
    path("customuser/", CustomUserCreate.as_view(), name="photo"),
    path("updateuser/", UpdateProfile.as_view(), name="updateprofile"),
    path("", include(router.urls)),
]
