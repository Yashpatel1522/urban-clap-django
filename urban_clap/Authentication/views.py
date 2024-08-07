from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render
from .models import User, UserProfiles
from .serializers import (
    RegisterSerailzers,
    LoginSerailzers,
    AuthUserSerializer,
    ChangePasswordSerializer,
    ForgetPasswordSerializer,
    ProfileUpdateSerailzers,
    ProfileSerializer,
    PasswordResetConfrimSerializer,
    GetUserSerializer,
    UpdateProfileSerializer,
)
from rest_framework import generics, status, viewsets, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from .permissions import IsAdmin, IsCustomer, IsSeviceProvider, RoleReturn
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from datetime import datetime
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from rest_framework.pagination import PageNumberPagination

# Create your views here.


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerailzers


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerailzers


class ProfileView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.request.user.is_superuser:
            self.permission_classes = [IsAdmin]
        elif self.request.user.is_staff:
            self.permission_classes = [IsSeviceProvider]
        else:
            self.permission_classes = [IsCustomer]
        return super().get_permissions()

    def get(self, request):
        role = RoleReturn(request)
        message = f"Hello {role.capitalize()}"
        return Response({"message": message})


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_active=True, is_superuser=False)
    serializer_class = AuthUserSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ["list", "destroy", "retrieve"]:
            self.permission_classes = [IsAdmin]
        elif self.action in ["profile"]:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    @action(
        detail=False,
        methods=["GET", "PUT"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def profile(self, request):
        if request.method == "GET":
            user_serializer = self.get_serializer(request.user)
            return Response(user_serializer.data)
        elif request.method == "PUT":
            user_serializer = ProfileUpdateSerailzers(
                request.user, data=request.data, partial=True
            )
            if user_serializer.is_valid():
                user_serializer.save()
                request.user.profile_updated_at = datetime.now()
                request.user.save()
                return Response(user_serializer.data)
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            user.is_active = False
            user.save()
            return Response(
                {
                    "status": status.HTTP_200_OK,
                    "message": "User delete successfully",
                    "data": [],
                }
            )
        except Exception as error:
            print(error)
            return Response(
                {
                    "status": status.HTTP_404_NOT_FOUND,
                    "message": "Id not found this delete",
                }
            )


class ChangePasswordViewSet(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(
            data=request.data,
        )
        if serializer.is_valid():
            if not user.check_password(serializer.data.get("current_password")):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.set_password(serializer.data.get("new_password"))
            self.profile_updated_at = datetime.now()
            user.save()
            return Response(
                {
                    "status": status.HTTP_200_OK,
                    "message": "Password updated successfully",
                    "data": [],
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgetPasswordViewSet(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ForgetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            user = User.objects.get(username=username)
            token = default_token_generator.make_token(user)
            u_id = urlsafe_base64_encode(force_bytes(user.pk))

            return Response({"u_id": u_id, "token": token}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfrimView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfrimSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "password has been reset successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data.get("refresh"))
            token.blacklist()
            return Response(
                {
                    "status": status.HTTP_205_RESET_CONTENT,
                    "message": "Logout successfully",
                    "data": [],
                }
            )
        except Exception as err:
            return Response({"message": str(err)}, status=status.HTTP_400_BAD_REQUEST)


class ProfileList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validate_data["user"] = request.user.id
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        profiles = UserProfiles.objects.filter(user_id=request.user.id).first()
        serializer = ProfileSerializer(profiles, many=False)
        return Response(
            {
                "status": status.HTTP_200_OK,
                "message": "Photo Get sucessfully",
                "data": serializer.data,
            }
        )


class UserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = User.objects.filter(id=request.user.id).first()

        serializer = GetUserSerializer(user)

        return Response(
            {
                "status": status.HTTP_200_OK,
                "message": "User Get sucessfully",
                "data": serializer.data,
            }
        )


class CustomUserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = GetUserSerializer


class UpdateProfile(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UpdateProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # print(self.request.user.profile.all().values())
        return self.request.user

    def put(self, request, *args, **kwargs):
        print("data", request.data)
        print("files", request.FILES)
        return super().put(request, *args, **kwargs)


class CustomPaginatorClass(PageNumberPagination):
    page_size = 6
    page_query_param = "page"
    max_page_size = 100


class UserData(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.filter(is_active=True, is_superuser=False)
    serializer_class = UpdateProfileSerializer
    pagination_class = CustomPaginatorClass

    def get_queryset(self):
        search = self.request.query_params.get("search")
        type = self.request.query_params.get("type")
        # print(search)
        if type == "sp":
            if search:
                return self.queryset.filter(is_staff=True, username__icontains=search)
            else:
                return self.queryset.filter(is_staff=True)
        elif type == "customer":
            if search:
                return self.queryset.filter(
                    is_staff=False, is_superuser=False, username__icontains=search
                )

            else:
                return self.queryset.filter(is_staff=False, is_superuser=False)
