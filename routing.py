# routing.py
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from tu_app import consumers  # Reemplaza 'tu_app' con el nombre de tu aplicación Django

websocket_urlpatterns = [
    path('ws/peso/', consumers.PesoConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': URLRouter(websocket_urlpatterns),
    # Puedes agregar otros protocolos aquí
})
