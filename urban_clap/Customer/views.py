from django.shortcuts import render
from rest_framework import status, viewsets
from .models import Appointment, Review
from Service_Provider.models import Services, Slots, Categories
from .serializer import (
    AppointmentSerializer,
    ReviewSerializer,
    AppointmentSerializerReader,
    SlotSerializer,
    ReviewSerializerForRead,
)
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from Authentication.permissions import (
    IsAdmin,
    RoleReturn,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from Service_Provider.response import CustomResponse
from datetime import time
from rest_framework.views import APIView
from django.db.models.functions import TruncMonth
from django.db.models import Count
from Service_Provider.views import CustomPaginatorClass
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.decorators import api_view
from Authentication.models import User

# yashvachhani


class AppointmentView(viewsets.ModelViewSet):

    authentication_classes = [JWTAuthentication]

    serializer_class = AppointmentSerializer
    queryset = Appointment.objects.all()
    # print(queryset)

    def get_permissions(self):
        if self.action in ["destroy"]:
            self.permission_classes = [IsAdmin]
        elif self.action in ["create", "update", "partial_update", "list", "retrieve"]:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        try:
            if self.request.user.is_superuser:
                return self.queryset
            elif self.request.user.is_staff:
                service = Services.objects.filter(user=self.request.user.id)
                return Appointment.objects.filter(
                    service__in=service, work_date__gte=timezone.now().date()
                )

            else:
                return self.queryset.filter(user=self.request.user)
        except Exception as err:
            return []

    def create(self, request):
        try:
            if self.request.method == "POST":
                user = self.request.user.id
                request.data["user"] = user
                serializer = AppointmentSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    self.notify_service_providers(serializer.instance)

                    print("yes")
                    return Response(
                        {
                            "data": serializer.data,
                            "message": "Add Data Successfully...!",
                        },
                        status=status.HTTP_201_CREATED,
                    )

                else:
                    return Response(
                        {
                            "data": serializer.errors,
                            "message": "Please Enter Valid Data...!",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                    # return CustomResponse(
                    #     serializer.errors, "Please Enter Valid Data...!"
                    # )
        except Exception as err:
            return Response(
                {
                    "data": [],
                    "message": str(err),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            # return CustomResponse("", str(err))

    def notify_service_providers(self, appointment):
        # channel_layer = get_channel_layer()
        # # Notify all connected WebSocket clients
        # print(appointment.id, appointment.service.user.username, "apppp")
        # async_to_sync(channel_layer.group_send)(
        #     "notifications",
        #     {
        #         "type": "send_notification",
        #         "message": f"New appointment booked: {appointment.id} for service provider {appointment.service.user.username}",
        #     },
        # )
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"service_provider_{appointment.service.user.id}",
            {
                "type": "send_notification",
                "message": f"New appointment booked by {appointment.user.username} for {appointment.service.description} on {appointment.work_date}.",
            },
        )


class AppointmentReader(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    serializer_class = AppointmentSerializerReader
    queryset = Appointment.objects.all()
    # pagination_class = CustomPaginatorClass

    def get_permissions(self):
        if self.action in ["destroy"]:
            self.permission_classes = [IsAdmin]
        elif self.action in ["create", "update", "partial_update", "list", "retrieve"]:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        is_cancel = bool(self.request.query_params.get("is_cancel"))
        is_future = bool(self.request.query_params.get("is_future"))
        is_accept = bool(self.request.query_params.get("is_accept"))
        print(is_accept, is_cancel, is_future)
        try:
            if self.request.user.is_superuser:
                return self.queryset
            elif self.request.user.is_staff:
                service = Services.objects.filter(user=self.request.user.id)
                if is_future:
                    return Appointment.objects.filter(
                        service__in=service,
                        work_date__gte=timezone.now().date(),
                        is_accept=is_accept,
                        is_cancel=is_cancel,
                        is_service_completed=False,
                        is_user_cancel=False,
                        # work_date__icontains=search,
                    )
                else:
                    return Appointment.objects.filter(
                        service__in=service,
                        work_date__lt=timezone.now().date(),
                        is_accept=is_accept,
                        is_cancel=is_cancel,
                        is_user_cancel=False,
                        # work_date__icontains=search,
                        # is_service_completed=False,
                    )

            else:

                return self.queryset.filter(user=self.request.user.id)
        except Exception as err:
            return []


class Reviewe(viewsets.ModelViewSet):
    parser_class = [MultiPartParser, FormParser]
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        id = self.request.query_params.get("serviceid")
        if id:
            service = Services.objects.filter(id=id)
            print(service)
            queryset = Review.objects.filter(service__in=service).all()
            print(queryset)
            serializer = self.get_serializer(queryset, many=True)

            return CustomResponse(serializer.data, "Get Reviews Successfully")


class SlotView(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    serializer_class = SlotSerializer
    pagination_class = CustomPaginatorClass
    queryset = list(Slots.objects.all())

    def get_permissions(self):
        if self.action in ["destroy"]:
            self.permission_classes = [IsAdmin]
        if self.action in [
            "create",
            "update",
            "partial_update",
            "list",
            "retrieve",
            "destroy",
        ]:

            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):

        slot = self.request.query_params.get("search")
        if self.request.user.is_staff:
            if slot:
                return Slots.objects.filter(
                    user=self.request.user.id, slot__icontains=slot
                )
            else:
                return Slots.objects.filter(user=self.request.user.id)

    def create(self, request):
        try:
            if self.request.method == "POST":
                user = self.request.user.id
                request.data["user"] = user
                serializer = SlotSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()

                    return CustomResponse(serializer.data, "Add Data Successfully...!")

                else:

                    return CustomResponse(
                        serializer.errors, "Please Enter Valid Data...!"
                    )
        except Exception as err:

            return CustomResponse("", str(err))


class AppointmentStatusChart(APIView):
    def get(self, request, format=None):
        data = (
            Appointment.objects.annotate(month=TruncMonth("work_date"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )
        months = [entry["month"].strftime("%B %Y") for entry in data]
        counts = [entry["count"] for entry in data]

        status_counts = Appointment.objects.values("is_accept", "is_cancel").annotate(
            count=Count("id")
        )

        status_data = {"Approved": 0, "Rejected": 0}

        for entry in status_counts:
            if entry["is_accept"]:
                status_data["Approved"] += entry["count"]
            if entry["is_cancel"]:
                status_data["Rejected"] += entry["count"]

        data2 = (
            Appointment.objects.values("service__description")
            .annotate(count=Count("id"))
            .order_by("service__description")
        )
        services = [entry["service__description"] for entry in data2]
        counts2 = [entry["count"] for entry in data2]

        # return Response()

        return Response(
            [
                {"status_data": status_data},
                {"months": months, "counts": counts},
                {"services": services, "counts": counts2},
            ]
        )


# only for getting all slot in dropdowon list
class CreateSlotDropDowonView(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    serializer_class = SlotSerializer
    # pagination_class = CustomPaginatorClass

    queryset = list(Slots.objects.all())

    def get_permissions(self):
        if self.action in ["destroy"]:
            self.permission_classes = [IsAdmin]
        if self.action in [
            "create",
            "update",
            "partial_update",
            "list",
            "retrieve",
            "destroy",
        ]:

            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):

        if self.request.user.is_staff:
            return Slots.objects.filter(user=self.request.user.id)


class AppointmentReaderPagination(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    serializer_class = AppointmentSerializerReader
    queryset = Appointment.objects.all()
    pagination_class = CustomPaginatorClass

    def get_permissions(self):
        if self.action in ["destroy"]:
            self.permission_classes = [IsAdmin]
        elif self.action in ["create", "update", "partial_update", "list", "retrieve"]:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        is_cancel = bool(self.request.query_params.get("is_cancel"))
        is_future = bool(self.request.query_params.get("is_future"))
        is_accept = bool(self.request.query_params.get("is_accept"))
        # print(is_accept, is_cancel, is_future)
        try:
            if self.request.user.is_superuser or (
                self.request.user.is_superuser == False
                and self.request.user.is_staff == False
            ):
                user = self.request.query_params.get("user")
                search = self.request.query_params.get("search")
                print(search)
                if user:
                    return self.queryset.filter(
                        user_id=user, work_date__icontains=search
                    )
                else:
                    print("else")
                    return self.queryset.filter(
                        user=self.request.user.id,
                        work_date__icontains=search,
                    )

            elif self.request.user.is_staff:
                service = Services.objects.filter(user=self.request.user.id)
                if is_future:
                    return Appointment.objects.filter(
                        service__in=service,
                        work_date__gte=timezone.now().date(),
                        is_accept=is_accept,
                        is_cancel=is_cancel,
                        is_service_completed=False,
                        # work_date__icontains=search,
                    )
                else:
                    return Appointment.objects.filter(
                        service__in=service,
                        work_date__lt=timezone.now().date(),
                        is_accept=is_accept,
                        is_cancel=is_cancel,
                        # work_date__icontains=search,
                        # is_service_completed=False,
                    )

            else:
                return self.queryset.filter(user=self.request.user.id)
        except Exception as err:
            return []


class ReadReviewe(viewsets.ModelViewSet):
    parser_class = [MultiPartParser, FormParser]
    queryset = Review.objects.all()
    serializer_class = ReviewSerializerForRead
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        id = self.request.query_params.get("serviceid")
        if id:
            service = Services.objects.filter(id=id)
            print(service)
            queryset = Review.objects.filter(service__in=service).all()
            print(queryset)
            serializer = self.get_serializer(queryset, many=True)

            return CustomResponse(serializer.data, "Get Reviews Successfully")


from django.utils.timezone import now
from django.db.models import Q, Count


@api_view(["GET"])
def top_service_providers(request, format=None):
    start_date = now().replace(day=1)
    top_providers = (
        Appointment.objects.filter(work_date__gte=start_date)
        .values("service__user__username")
        .annotate(booking_count=Count("service"))
        .order_by("-booking_count")[:10]
    )

    service_provider_count = User.objects.filter(is_staff=True, is_active=True)
    customer_count = User.objects.filter(is_staff=False, is_active=True)
    category_count = Categories.objects.filter()

    return Response(
        {
            "top_providers": top_providers,
            "sp_count": len(list(service_provider_count)),
            "cs_count": len(list(customer_count)),
            "c_count": len(list(category_count)),
        }
    )
