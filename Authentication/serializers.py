from rest_framework import serializers, validators, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import Token
from .models import User, UserProfiles
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .helper import DataResponse
from django.utils.http import urlsafe_base64_decode
import re
from datetime import datetime
from django.contrib.auth.tokens import default_token_generator

# Vishvas Panshiniya


class RegisterSerailzers(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(
        required=True,
        validators=[validators.UniqueValidator(queryset=User.objects.filter())],
    )
    username = serializers.CharField(
        required=True,
        validators=[validators.UniqueValidator(queryset=User.objects.all())],
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "contact",
            "password",
            "password2",
            "username",
            "address",
            "is_staff",
        )
        extra_kwargs = {
            "password": {"write_only": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "email": {"required": True},
            "contact": {"required": True},
            "username": {"required": True},
            "address": {"required": True},
            "is_staff": {"required": True},
        }

    def validate_first_name(self, value):
        if not re.match("^[a-zA-Z ]*$", value):
            raise serializers.ValidationError(
                "First Name can only contain letters and spaces."
            )
        return value

    def validate_last_name(self, value):
        if not re.match("^[a-zA-Z ]*$", value):
            raise serializers.ValidationError(
                "Last Name can only contain letters and spaces."
            )
        return value

    def validate_contact(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError(
                "Contact number must be digit and 10 digit."
            )
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data["email"],
            contact=validated_data["contact"],
            username=validated_data["username"],
            address=validated_data["address"],
            is_staff=validated_data["is_staff"],
        )

        user.set_password(validated_data["password"])
        user.save()

        return user


class ProfileUpdateSerailzers(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "contact", "username", "address")

        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
            "email": {"required": False},
            "contact": {"required": False},
            "username": {"required": False},
            "address": {"required": False},
        }

    def validate_first_name(self, value):
        if not re.match("^[a-zA-Z ]*$", value):
            raise serializers.ValidationError(
                "First Name can only contain letters and spaces."
            )
        return value

    def validate_last_name(self, value):
        if not re.match("^[a-zA-Z ]*$", value):
            raise serializers.ValidationError(
                "Last Name can only contain letters and spaces."
            )
        return value

    def validate_contact(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError(
                "Contact number must be digit and 10 digit."
            )
        return value


class LoginSerailzers(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # token["username"] = user.username
        # token["id"] = user.id
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data["is_staff"] = user.is_staff
        data["is_superuser"] = user.is_superuser
        data["username"] = user.username

        return data


class UserProfilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfiles
        fields = ["profile_photo"]


class AuthUserSerializer(serializers.ModelSerializer):
    # user_profile = UserProfilesSerializer(source="userprofile", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "username",
            "is_active",
            "is_staff",
            "contact",
            "address",
            # "user_profile",
        )
        read_only_fields = ("id", "is_active", "is_staff")


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"new_password": "New password fields didn't match."}
            )
        return attrs


class ForgetPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)

    def validate_username(self, value):
        if not User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is not register")
        return value


class PasswordResetConfrimSerializer(serializers.Serializer):
    u_id = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, data):
        try:
            u_id = urlsafe_base64_decode(data["u_id"]).decode()
            user = User.objects.get(pk=u_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("invalid userid")

        if not default_token_generator.check_token(user, data["token"]):
            raise serializers.ValidationError("invalid token")
        return data

    def save(self):
        u_id = urlsafe_base64_decode(self.validated_data["u_id"]).decode()
        user = User.objects.get(pk=u_id)
        user.set_password(self.validated_data["new_password"])
        user.save()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfiles
        fields = ["profile_photo"]
        # depth = 1


class GetUserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(
        required=True,
        validators=[validators.UniqueValidator(queryset=User.objects.filter())],
    )
    username = serializers.CharField(
        required=True,
        validators=[validators.UniqueValidator(queryset=User.objects.all())],
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "contact",
            "address",
            "password2",
            "is_staff",
            "password",
            "profile",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "email": {"required": True},
            "contact": {"required": True},
            "username": {"required": True},
            "address": {"required": True},
            "is_staff": {"required": True},
            "profile": {"required": True},
        }

    def validate_first_name(self, value):
        if not re.match("^[a-zA-Z ]*$", value):
            raise serializers.ValidationError(
                "First Name can only contain letters and spaces."
            )
        return value

    def validate_last_name(self, value):
        if not re.match("^[a-zA-Z ]*$", value):
            raise serializers.ValidationError(
                "Last Name can only contain letters and spaces."
            )
        return value

    def validate_contact(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError(
                "Contact number must be digit and 10 digit."
            )
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        return attrs

    def create(self, validate_data):
        profile_data = validate_data.pop("profile", {})
        password = validate_data.pop("password")
        validate_data.pop("password2")
        user = User.objects.create_user(password=password, **validate_data)
        UserProfiles.objects.create(user=user, **profile_data)
        return user


class ProfileSerializer2(serializers.ModelSerializer):
    profile_photo = serializers.ImageField(required=False)

    class Meta:
        model = UserProfiles
        fields = ["profile_photo", "user"]
        extra_kwargs = {
            "user": {"write_only": True},
        }


class UpdateProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer2(required=False, many=True)

    class Meta:
        model = User
        fields = [
            "pk",
            "username",
            "email",
            "first_name",
            "last_name",
            "contact",
            "address",
            "profile",
            "is_active",
            "is_staff",
        ]
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
            "email": {"required": False},
            "contact": {"required": False},
            "username": {"required": False},
            "address": {"required": False},
            "profile": {"required": False},
        }

    def update(self, instance, validate_data):
        # print("self data", self.request.data)
        # print("Profile_data", self.__dict__)
        # print(self.data)
        print("asdasdasd", instance)
        print("asdasdasd", validate_data)
        Profile_data = self.validated_data.pop("profile", {})
        profile_photo = self.context["request"].FILES.get("profile.profile_photo")

        instance.first_name = validate_data.get("first_name", instance.first_name)
        instance.last_name = validate_data.get("last_name", instance.last_name)
        instance.username = validate_data.get("username", instance.username)
        instance.email = validate_data.get("email", instance.email)
        instance.contact = validate_data.get("contact", instance.contact)
        instance.address = validate_data.get("address", instance.address)
        instance.save()

        if profile_photo:
            demo = ProfileSerializer2(
                data={
                    "profile_photo": self.context["request"].FILES.get(
                        "profile.profile_photo"
                    ),
                    "user": self.context["request"].user.pk,
                },
                instance=UserProfiles.objects.filter(
                    user=self.context["request"].user
                ).first(),
            )
            print(demo.is_valid())
            print(demo.errors)
            demo.save()
        return instance
