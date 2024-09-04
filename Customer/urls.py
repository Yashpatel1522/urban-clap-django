"""
URL configuration for urban_clap project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"appointment", views.AppointmentView, basename="appointment")
router.register(
    r"appointmentreader", views.AppointmentReader, basename="appointmentreader"
)
router.register(
    r"appointmentpagination",
    views.AppointmentReaderPagination,
    basename="paginationappointment",
)
router.register(r"review", views.Reviewe, basename="review")
router.register(r"readreview", views.ReadReviewe, basename="readreview")
router.register(r"slot", views.SlotView, basename="slot")
router.register(r"allslot", views.CreateSlotDropDowonView, basename="slots")

urlpatterns = [
    path(
        "appointment-status-chart/",
        views.AppointmentStatusChart.as_view(),
        name="appointment-status-chart",
    ),
    path("top-service-providers/", views.top_service_providers, name="top_sp"),
]

urlpatterns += router.urls
