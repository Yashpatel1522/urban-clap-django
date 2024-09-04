from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"services", views.ServicesView, basename="services")
# router.register(r"ser",views.SortigReviwWise,basename="ser")
# yashvachhani
urlpatterns = [
    path("category/", views.CatogoryView.as_view(), name="category"),
    path("allcategory/", views.DropDowonCatogoryView.as_view(), name="allcategory"),
    path(
        "category/<int:id>",
        views.get_specific_category_data,
        name="specificcetegorydata",
    ),
    path("service-filter/", views.SortigReviwWise.as_view()),
    path("service-searching/", views.Searching.as_view()),
    path("csv/", views.genrate_csv_report, name="csv"),
    path("csvdataview/", views.genrate_csv_data, name="csvdataview"),
    path("pdf/", views.genrate_pdf_report, name="pdf"),
]

urlpatterns += router.urls
