from django.contrib import admin
from .models import User, UserProfiles

# Register your models here.


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "profile_photo"]


admin.site.register(UserProfiles, ProfileAdmin)
