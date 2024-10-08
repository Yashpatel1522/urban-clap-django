from rest_framework import serializers
from .models import Services, Categories
import re


# yashvachhani
class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Services
        fields = "__all__"

    def validate_description(self, description):
        if description.strip() != "":
            if not re.match("^[A-Z a-z]*$", description):
                raise serializers.ValidationError(
                    "Ivlaid Description Only character Allowed"
                )
            return description
        else:
            raise serializers.ValidationError("Empty Descriptions...!")

    def validate_price(self, price):
        if int(price) == 0:
            raise serializers.ValidationError("Price must be greater 0")
        return price


# yashvachhani
class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Categories
        fields = "__all__"

    def validate_name(self, name):
        if name.strip() != "":
            if not re.match("^[A-Z a-z]*$", name):
                raise serializers.ValidationError("Ivlaid Name Only character Allowed")
            return name
        raise serializers.ValidationError("Empty Catagory Name...!")


class SelectedServiceData(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = "__all__"
