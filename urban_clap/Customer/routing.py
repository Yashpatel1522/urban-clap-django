from django.urls import path
from .consumers import NotificationConsumer

websocket_urlpatterns = [
    # path("ws/notifications/", NotificationConsumer.as_asgi()),
    path("ws/notifications/<str:service_provider_id>/", NotificationConsumer.as_asgi()),
]
