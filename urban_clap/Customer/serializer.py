from rest_framework import serializers
from .models import Appointment, Review, ReviewPhotos, Services, Slots
import time
from datetime import date
from django.db import models

today = date.today()


# yashvachhani
class AppointmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Appointment
        fields = "__all__"

    def validate_work_date(self, work_date):
        if work_date:
            if work_date > today:
                return work_date
            raise serializers.ValidationError("Invalid Date...!")


class AppointmentSerializerReader(serializers.ModelSerializer):

    class Meta:
        model = Appointment
        fields = "__all__"
        depth = 1


class ReviewPhotosSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReviewPhotos
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):

    images = ReviewPhotosSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(write_only=True),
        write_only=True,
    )

    class Meta:
        model = Review
        fields = ["service", "rating", "comment", "images", "uploaded_images"]

    def create(self, validated_data):
        user = self.context.get("request").user
        uploaded_images = validated_data.pop("uploaded_images")
        print(uploaded_images)
        product = Review.objects.create(**validated_data, user=user)

        for image in uploaded_images:
            ReviewPhotos.objects.create(
                review=product, media=image, mime_type=image.content_type
            )
        return product


class ReviewFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"


class ServiceFilterSerializer(serializers.ModelSerializer):
    review = ReviewFilterSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Services
        fields = "__all__"
        depth = 1

    def get_average_rating(self, obj):
        review = obj.reviews.all()
        if review.exists():
            return review.aggregate(models.Avg("rating"))["rating__avg"]


class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slots
        fields = "__all__"


class ReviewSerializerForRead(serializers.ModelSerializer):

    images = ReviewPhotosSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True,
    )

    class Meta:
        model = Review
        fields = ["service", "rating", "comment", "images", "uploaded_images", "user"]
        depth = 1


class AppointmentSerializerReaderForCSV(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.description")
    provider_name = serializers.CharField(source="service.user.username")
    user_name = serializers.CharField(source="user.username")
    area_s = serializers.CharField(source="area.name")
    slot_s = serializers.CharField(source="slot.slot")

    class Meta:
        model = Appointment
        fields = [
            "user",
            "service",
            "area",
            "slot",
            "work_date",
            "is_accept",
            "is_cancel",
            "created_at",
            "updated_at",
            "is_service_completed",
            "is_user_cancel",
            "service_name",
            "provider_name",
            "user_name",
            "area_s",
            "slot_s",
        ]
        depth = 1
