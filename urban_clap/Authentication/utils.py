# from django.contrib.auth import authenticate, get_user_model
# from rest_framework import serializers
# from Authentication.models import User


# # def create(self, validated_data):
# #     user = User.objects.create(
# #         first_name=validated_data['first_name'],
# #         last_name=validated_data['last_name'],
# #         email=validated_data['email'],
# #         contact=validated_data['contact'],
# #         username=validated_data['username'],
# #         address=validated_data['address'],
# #         is_staff=validated_data['is_staff'],
# #     )

# #     user.set_password(validated_data['password'])
# #     user.save()

# #     return user

# def create_user_account(email, password, first_name="",
#                         last_name="", contact="", username="", address="", is_staff=""):
#     user = get_user_model().objects.create_user(
#         email=email, password=password, first_name=first_name,
#         last_name=last_name, contact=contact, username=username, address=address, is_staff=is_staff)
#     return user
