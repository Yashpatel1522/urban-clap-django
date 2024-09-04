from django.db import models
from Service_Provider.models import Services, Area, Slots
from Authentication.models import User

# Create your models here.


# yashvchhani
class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Services, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, blank=True)
    slot = models.ForeignKey(Slots, on_delete=models.DO_NOTHING)
    work_date = models.DateField()
    is_accept = models.BooleanField(default=False)
    is_cancel = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_service_completed = models.BooleanField(default=False)
    is_user_cancel = models.BooleanField(default=False)


class Review(models.Model):
    service = models.ForeignKey(
        Services, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    comment = models.CharField(max_length=100)


class ReviewPhotos(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, null=True, related_name="images"
    )
    media = models.ImageField(upload_to="Review")
    mime_type = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
