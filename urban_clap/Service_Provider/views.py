from django.shortcuts import render, HttpResponse
from .serializer import ServiceSerializer, CategorySerializer, SelectedServiceData
from rest_framework.views import APIView
from rest_framework import status, viewsets, generics
from rest_framework.response import Response
from .models import Categories, Services
from .customerenderer import CustomJSONRenderer
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from Authentication.permissions import (
    IsAdmin,
    IsCustomer,
    IsSeviceProvider,
    RoleReturn,
    IsAdminOrServiceProvider,
    IsAllRole,
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator
from django.db.models import Count, Avg
from Customer.serializer import ServiceFilterSerializer
from .response import CustomResponse
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
from Customer.models import Appointment
from Customer.serializer import AppointmentSerializerReaderForCSV
import csv
from rest_framework.decorators import api_view
from django.http import FileResponse

from io import StringIO, BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


# Create your views here.
# yashvachhani
class CustomPaginatorClass(PageNumberPagination):
    # print("yes")
    page_size = 2
    page_query_param = "page"
    max_page_size = 100


class ServicesView(viewsets.ModelViewSet):
    renderer_classes = [CustomJSONRenderer]
    authentication_classes = [JWTAuthentication]
    serializer_class = ServiceSerializer
    queryset = Services.objects.all()
    pagination_class = CustomPaginatorClass

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ["create", "update", "destroy", "partial_update"]:
            self.permission_classes = [IsAdminOrServiceProvider]
        else:
            self.permission_classes = [IsAdminOrServiceProvider]
        return super().get_permissions()

    def get_queryset(self):
        description = self.request.query_params.get("search")
        user = self.request.query_params.get("user")
        q = ""
        if description:
            if user:
                if self.request.user.is_superuser:
                    q = self.queryset.filter(
                        user_id=user, description__icontains=description
                    ).order_by("pk")

            else:
                if self.request.user.is_superuser:
                    q = self.queryset.filter(
                        description__icontains=description
                    ).order_by("pk")
                elif self.request.user.is_staff:
                    q = self.queryset.filter(
                        user=self.request.user.id, description__icontains=description
                    ).order_by("pk")
                else:
                    q = self.queryset.filter(
                        status=True, description__icontains=description
                    ).order_by("pk")

        else:
            if user:
                if self.request.user.is_superuser:
                    q = self.queryset.filter(user_id=user).order_by("pk")
            else:
                if self.request.user.is_superuser:
                    q = self.queryset
                elif self.request.user.is_staff:
                    q = self.queryset.filter(user=self.request.user.id).order_by("pk")
                else:
                    q = self.queryset.filter(status=True).order_by("pk")
        return q

    def create(self, request):
        if self.request.method == "POST":
            user = self.request.user.id
            request.data["user"] = user
            # request.data["category_id"]=request.data["category"]

            serializer = ServiceSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                return CustomResponse(serializer.data, "Add Data Successfully...!")
            else:

                return CustomResponse(serializer.errors, "Please Enter Valid Data...!")


class CatogoryView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.request.method in ["POST", "PATCH"]:
            self.permission_classes = [
                IsAdminOrServiceProvider,
            ]
        elif self.request.method == "DELETE":
            self.permission_classes = [
                IsAdmin,
            ]
        else:
            self.permission_classes = [
                IsAdminOrServiceProvider,
            ]
        return super().get_permissions()

    # yashvachhani

    def get(self, request):
        try:
            queryset = Categories.objects.all().order_by("pk")
            name = self.request.query_params.get("search")
            if name:
                queryset = queryset.filter(name__icontains=name)

            Paginator = CustomPaginatorClass()
            result_page = Paginator.paginate_queryset(queryset, request)
            serializer = CategorySerializer(result_page, many=True)
            return Paginator.get_paginated_response(serializer.data)

        except Categories.DoesNotExist:
            return CustomResponse("", "Empty Data...!")

    # yashvachhani
    def post(self, request):
        try:
            category_model_data = request.data
            category_serializer_data = CategorySerializer(data=category_model_data)

            if not category_serializer_data.is_valid():

                return CustomResponse("", category_serializer_data.errors)
            category_serializer_data.save()

            return CustomResponse(
                category_serializer_data.data, "Category Added Successfully...!"
            )

        except Exception as err:

            return CustomResponse("", str(err))

    # yash vachhani
    def patch(self, request):
        try:
            id = self.request.query_params.get("id")
            try:
                data = Categories.objects.get(pk=id)
                update_data = CategorySerializer(data, data=request.data, partial=True)
                if not update_data.is_valid():

                    return CustomResponse("", update_data.errors)

                update_data.save()

                return CustomResponse(
                    update_data.data, "Update Category Successfully...!"
                )

            except Categories.DoesNotExist:

                return CustomResponse("", "Invalid Category Id")
        except Exception as err:

            return CustomResponse("", str(err))

    # yash vachhani
    def delete(self, request):
        id = self.request.query_params.get("id")

        try:
            data = Categories.objects.get(pk=id)
            if data:
                data.delete()

                return CustomResponse("", "Category Deleted...!")

        except Exception as err:

            return CustomResponse("", str(err))


@api_view(["GET"])
def get_specific_category_data(request, id, format=None):
    data = Services.objects.filter(category_id=id)

    if not data:
        return CustomResponse("", "Invalid Id...!")

    if request.method == "GET":
        serializer = SelectedServiceData(data, many=True)

        return CustomResponse(serializer.data, "Get Data Successfully...!")


class SortigReviwWise(generics.ListAPIView):
    queryset = Services.objects.annotate(
        average_rating=Avg("reviews__rating", default=0),
    ).order_by("-average_rating")
    serializer_class = ServiceFilterSerializer
    pagination_class = CustomPaginatorClass

    def get_queryset(self):
        search = self.request.query_params.get("search")
        if search:
            return self.queryset.filter(description__icontains=search)
        else:
            return self.queryset


class Searching(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        services = Services.objects.filter(
            description__icontains=request.query_params.get("service"),
            user=request.user,
        )
        serializer = SelectedServiceData(services, many=True)

        return Response(
            {
                "status": status.HTTP_200_OK,
                "message": "Get Data sucessfully",
                "data": serializer.data,
            }
        )


# for drop dowon all category
class DropDowonCatogoryView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.request.method in ["POST", "PATCH"]:
            self.permission_classes = [
                IsAdminOrServiceProvider,
            ]
        elif self.request.method == "DELETE":
            self.permission_classes = [
                IsAdmin,
            ]
        else:
            self.permission_classes = [
                IsAdminOrServiceProvider,
            ]
        return super().get_permissions()

    # yashvachhani

    def get(self, request):
        try:
            category_data = Categories.objects.all()
            category_serialize_data = CategorySerializer(category_data, many=True)

            return CustomResponse(
                category_serialize_data.data, "Get Category Data Successfully...!"
            )
        except Categories.DoesNotExist:
            return CustomResponse("", "Empty Data...!")


# create csv for reports


@api_view(["GET"])
def genrate_csv_report(request):
    start_date = parse_date(request.GET.get("start_date"))
    end_date = parse_date(request.GET.get("end_date"))
    if start_date and end_date:

        appointments = Appointment.objects.filter(
            work_date__range=(start_date, end_date)
        )
        serializer = AppointmentSerializerReaderForCSV(appointments, many=True)

        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)
        # print(writer)
        writer.writerow(
            ["service", "service provider", "user", "area", "slot", "work_date"]
        )

        for app in serializer.data:
            writer.writerow(
                [
                    app["service_name"],
                    app["provider_name"],
                    app["user_name"],
                    app["area_s"],
                    app["slot_s"],
                    app["work_date"],
                ]
            )
        print(type(csv_buffer.getvalue()))
        response = HttpResponse(csv_buffer.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="report_{start_date}_to_{end_date}.csv"'
        )
        return response
    else:
        return Response(status=400)


from django.template.loader import render_to_string
import tempfile
from weasyprint import HTML
import logging


@api_view(["GET"])
def genrate_pdf_report(request):
    start_date = parse_date(request.GET.get("start_date"))
    end_date = parse_date(request.GET.get("end_date"))
    if start_date and end_date:
        appointments = Appointment.objects.filter(
            work_date__range=(start_date, end_date)
        )
        serializer = AppointmentSerializerReaderForCSV(appointments, many=True)

        html_string = render_to_string(
            "pages/report.html",
            {
                "appointments": serializer.data,
                "start_date": start_date,
                "end_date": end_date,
            },
        )

        pdf_buffer = BytesIO()
        HTML(string=html_string).write_pdf(pdf_buffer)

        pdf_buffer.seek(0)

        response = HttpResponse(
            pdf_buffer.getvalue(),
            content_type="application/pdf",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="report_{start_date}_{end_date}.pdf"'
        )
        response["Content-Encoding"] = "identity"
        response["Buffering"] = "no-cache"
        return response

    else:
        return Response(status=400)


@api_view(["GET"])
def genrate_csv_data(request):
    start_date = parse_date(request.GET.get("start_date"))
    end_date = parse_date(request.GET.get("end_date"))
    if start_date and end_date:

        appointments = Appointment.objects.filter(
            work_date__range=(start_date, end_date)
        )
        serializer = AppointmentSerializerReaderForCSV(appointments, many=True)
        return Response(serializer.data)
    else:
        return Response(status=400)
